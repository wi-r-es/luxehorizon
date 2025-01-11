



/*
███████ ██████           ██████ ██████  ███████  █████  ████████ ███████         ██████  ███████ ███████ ███████ ██████  ██    ██  █████  ████████ ██  ██████  ███    ██ 
██      ██   ██         ██      ██   ██ ██      ██   ██    ██    ██              ██   ██ ██      ██      ██      ██   ██ ██    ██ ██   ██    ██    ██ ██    ██ ████   ██ 
███████ ██████          ██      ██████  █████   ███████    ██    █████           ██████  █████   ███████ █████   ██████  ██    ██ ███████    ██    ██ ██    ██ ██ ██  ██ 
     ██ ██              ██      ██   ██ ██      ██   ██    ██    ██              ██   ██ ██           ██ ██      ██   ██  ██  ██  ██   ██    ██    ██ ██    ██ ██  ██ ██ 
███████ ██      ███████  ██████ ██   ██ ███████ ██   ██    ██    ███████ ███████ ██   ██ ███████ ███████ ███████ ██   ██   ████   ██   ██    ██    ██  ██████  ██   ████ 
*/


CREATE OR REPLACE PROCEDURE sp_create_reservation( --TESTED
    user_id INTEGER,
    room_id INTEGER,
    checkin DATE,
    checkout DATE,
    guests INTEGER
)
AS $$
DECLARE
    reservation_id INTEGER;
    total_price NUMERIC;
    nights INTEGER;
    room_base_price NUMERIC;
    season_rate NUMERIC;
    season_id INTEGER;
BEGIN
    -- Verify if the room exists
    IF NOT EXISTS (SELECT 1 FROM "room_management.room" WHERE id = room_id) THEN
        RAISE EXCEPTION 'Room not found.';
    END IF;

    -- Calculate the number of nights
    nights := checkout - checkin;

    IF nights <= 0 THEN
        RAISE EXCEPTION 'The check-in and check-out dates are not valid.';
    END IF;

    -- Determine the season ID and highest season rate for the reservation period
    SELECT id, MAX(rate) INTO season_id, season_rate
    FROM "finance.season"
    WHERE 
        (
            -- Non-year-spanning seasons
            (begin_month < end_month OR (begin_month = end_month AND begin_day <= end_day))
            AND make_date(EXTRACT(YEAR FROM checkin)::INTEGER, begin_month, begin_day) <= checkout
            AND make_date(EXTRACT(YEAR FROM checkin)::INTEGER, end_month, end_day) >= checkin
        )
        OR
        (
            -- Year-spanning seasons
            (begin_month > end_month OR (begin_month = end_month AND begin_day > end_day))
            AND (
                checkin >= make_date(EXTRACT(YEAR FROM checkin)::INTEGER, begin_month, begin_day)
                OR checkout <= make_date(EXTRACT(YEAR FROM checkin)::INTEGER, end_month, end_day)
            )
        )
    GROUP BY id;

    IF season_id IS NULL THEN
        RAISE EXCEPTION 'No valid season found for the specified dates.';
    END IF;

    -- Get price for the room
    SELECT base_price INTO room_base_price
    FROM "room_management.room"
    WHERE id = room_id;

    IF room_base_price IS NULL THEN
        RAISE EXCEPTION 'Room price is not defined.';
    END IF;

    -- Calculate final price
    total_price := (nights * (room_base_price + season_rate));

    -- Create new reservation
    INSERT INTO "reserves.reservation" (client_id, begin_date, end_date, status, total_value, season_id)
    VALUES (user_id, checkin, checkout, 'P', total_price, season_id)
    RETURNING id INTO reservation_id;

    -- Relate rooms and reservation
    INSERT INTO "reserves.room_reservation" (reservation_id, room_id, price_reservation)
    VALUES (reservation_id, room_id, total_price);

    -- Confirm success
    RAISE NOTICE 'Reservation created successfully. Reservation ID: %, Season ID: %', reservation_id, season_id;
END;
$$ LANGUAGE plpgsql;







/*
███████ ██████          ██    ██ ██████  ██████   █████  ████████ ███████         ██████  ███████ ███████ ███████ ██████  ██    ██  █████  ████████ ██  ██████  ███    ██ 
██      ██   ██         ██    ██ ██   ██ ██   ██ ██   ██    ██    ██              ██   ██ ██      ██      ██      ██   ██ ██    ██ ██   ██    ██    ██ ██    ██ ████   ██ 
███████ ██████          ██    ██ ██████  ██   ██ ███████    ██    █████           ██████  █████   ███████ █████   ██████  ██    ██ ███████    ██    ██ ██    ██ ██ ██  ██ 
     ██ ██              ██    ██ ██      ██   ██ ██   ██    ██    ██              ██   ██ ██           ██ ██      ██   ██  ██  ██  ██   ██    ██    ██ ██    ██ ██  ██ ██ 
███████ ██      ███████  ██████  ██      ██████  ██   ██    ██    ███████ ███████ ██   ██ ███████ ███████ ███████ ██   ██   ████   ██   ██    ██    ██  ██████  ██   ████ 
*/
/*
 * Updates reservation details. 
 *
 *  All data sent is the data that is going to stay. 
 *  So if a room is added but none is deleted then all rooms must be sent either way otherwise only the new one will stay in the system
 */
CREATE OR REPLACE PROCEDURE sp_update_reservation( --TESTED
    _reservation_id INT,
    _new_begin_date DATE,
    _new_end_date DATE,
    _new_room_ids INT[]
)
LANGUAGE plpgsql
AS $$
DECLARE
    _room_id INT;
    _room_available BOOLEAN;
    _season_id INT;
    _season_rate NUMERIC;
    _room_base_price NUMERIC;
    _total_price NUMERIC := 0;
    _current_begin_date DATE;
    _current_end_date DATE;
    nights INTEGER;
    msg TEXT;
    content TEXT;
    hint TEXT;
BEGIN
    -- Fetch the current reservation dates
    SELECT begin_date, end_date INTO _current_begin_date, _current_end_date
    FROM "reserves.reservation"
    WHERE id = _reservation_id;

    -- Validate reservation dates
    IF _new_begin_date >= _new_end_date THEN
        RAISE EXCEPTION 'Begin date must be earlier than end date.';
    END IF;

    -- Fetch season information based on new dates
    SELECT id, MAX(rate) INTO _season_id, _season_rate
    FROM "finance.season"
    WHERE 
        (
            -- Non-year-spanning seasons
            (begin_month < end_month OR (begin_month = end_month AND begin_day <= end_day))
            AND make_date(EXTRACT(YEAR FROM _new_begin_date)::INTEGER, begin_month, begin_day) <= _new_end_date
            AND make_date(EXTRACT(YEAR FROM _new_begin_date)::INTEGER, end_month, end_day) >= _new_begin_date
        )
        OR
        (
            -- Year-spanning seasons
            (begin_month > end_month OR (begin_month = end_month AND begin_day > end_day))
            AND (
                _new_begin_date >= make_date(EXTRACT(YEAR FROM _new_begin_date)::INTEGER, begin_month, begin_day)
                OR _new_end_date <= make_date(EXTRACT(YEAR FROM _new_begin_date)::INTEGER, end_month, end_day)
            )
        )
    GROUP BY id;

    IF _season_id IS NULL THEN
        RAISE EXCEPTION 'No valid season found for the selected dates.';
    END IF;

    -- Check new room availability
    FOR _room_id IN SELECT UNNEST(_new_room_ids) LOOP
        SELECT NOT EXISTS (
            SELECT 1 
            FROM "reserves.room_reservation" rr
            INNER JOIN "reserves.reservation" r ON rr.reservation_id = r.id
            WHERE rr.room_id = _room_id
              AND r.status IN ('P', 'C') -- Only consider Pending or Confirmed reservations
              AND r.id <> _reservation_id -- Exclude current reservation
              AND (
                  -- Overlap condition considering the new dates
                  r.begin_date < _new_end_date AND r.end_date > _new_begin_date
              )
        ) INTO _room_available;

        IF NOT _room_available THEN
            RAISE EXCEPTION 'Room id % is not available for the selected dates.', _room_id;
        END IF;
    END LOOP;

    -- Update reservation dates and season
    UPDATE "reserves.reservation"
    SET begin_date = _new_begin_date,
        end_date = _new_end_date,
        season_id = _season_id
    WHERE id = _reservation_id;

    -- Remove all existing room assignments for the reservation
    DELETE FROM "reserves.room_reservation" WHERE reservation_id = _reservation_id;

    -- Calculate the number of nights
    nights := _new_end_date - _new_begin_date;

    IF nights <= 0 THEN
        RAISE EXCEPTION 'The check-in and check-out dates are not valid.';
    END IF;

    -- Insert new room reservations and calculate total price
    FOR _room_id IN SELECT UNNEST(_new_room_ids) LOOP
        SELECT base_price INTO _room_base_price FROM "room_management.room" WHERE id = _room_id;

        IF _room_base_price IS NULL THEN
            RAISE EXCEPTION 'Base price not defined for room id %.', _room_id;
        END IF;

        INSERT INTO "reserves.room_reservation" (
            reservation_id, room_id, price_reservation
        ) VALUES (
            _reservation_id, _room_id, _room_base_price + _season_rate
        );

        -- Add to total price
        _total_price := _total_price + (_room_base_price + _season_rate);
    END LOOP;
    _total_price := _total_price * nights;
    -- Update the total price in the reservation
    UPDATE "reserves.reservation"
    SET total_value = _total_price
    WHERE id = _reservation_id;

    RAISE NOTICE 'Reservation id % updated successfully.', _reservation_id;

EXCEPTION WHEN OTHERS THEN
    GET STACKED DIAGNOSTICS msg = MESSAGE_TEXT,
                            content = PG_EXCEPTION_DETAIL,
                            hint = PG_EXCEPTION_HINT;
    CALL sp_secLogError(msg, hint, content);

    RAISE NOTICE E'--- Call content ---\n%', content;
END;
$$;



/*
███████ ██████           ██████  █████  ███    ██  ██████ ███████ ██     ████          ██████  ███████ ███████ ███████ ██████  ██    ██  █████  ████████ ██  ██████  ███    ██ 
██      ██   ██         ██      ██   ██ ████   ██ ██      ██      ██              ██   ██ ██      ██      ██      ██   ██ ██    ██ ██   ██    ██    ██ ██    ██ ████   ██ 
███████ ██████          ██      ███████ ██ ██  ██ ██      █████   ██              ██████  █████   ███████ █████   ██████  ██    ██ ███████    ██    ██ ██    ██ ██ ██  ██ 
     ██ ██              ██      ██   ██ ██  ██ ██ ██      ██      ██              ██   ██ ██           ██ ██      ██   ██  ██  ██  ██   ██    ██    ██ ██    ██ ██  ██ ██ 
███████ ██      ███████  ██████ ██   ██ ██   ████  ██████ ███████ ███████ ███████ ██   ██ ███████ ███████ ███████ ██   ██   ████   ██   ██    ██    ██  ██████  ██   ████ 
*/

/*
 * Cancel a reservation
 */
 
CREATE OR REPLACE PROCEDURE sp_cancel_reservation( --TESTED
    _reservation_id INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Verificar se a reserva existe
    IF NOT EXISTS (
        SELECT 1 
        FROM "reserves.reservation" 
        WHERE id = _reservation_id
    ) THEN
        RAISE EXCEPTION 'Reservation id % does not exist.', _reservation_id;
    END IF;

    -- Deletar associações com quartos
    DELETE FROM "reserves.room_reservation"
    WHERE reservation_id = _reservation_id;

    -- Atualizar o status da reserva para "Cancelado"
    UPDATE "reserves.reservation"
    SET status = 'CC'  -- Substituir 'CC' pelo código adequado se necessário
    WHERE id = _reservation_id;

    -- Mensagem de sucesso
    RAISE NOTICE 'Reservation id % cancelled successfully.', _reservation_id;

END;
$$;


/*
████████ ██████   ██████           ██████ ██   ██ ███████  ██████ ██   ██         ██████   ██████   ██████  ███    ███         
   ██    ██   ██ ██               ██      ██   ██ ██      ██      ██  ██          ██   ██ ██    ██ ██    ██ ████  ████         
   ██    ██████  ██   ███         ██      ███████ █████   ██      █████           ██████  ██    ██ ██    ██ ██ ████ ██         
   ██    ██   ██ ██    ██         ██      ██   ██ ██      ██      ██  ██          ██   ██ ██    ██ ██    ██ ██  ██  ██         
   ██    ██   ██  ██████  ███████  ██████ ██   ██ ███████  ██████ ██   ██ ███████ ██   ██  ██████   ██████  ██      ██ ███████ 
                                                                                                                              
 █████  ██    ██  █████  ██ ██       █████  ██████  ██ ██      ██ ████████ ██    ██ 
██   ██ ██    ██ ██   ██ ██ ██      ██   ██ ██   ██ ██ ██      ██    ██     ██  ██  
███████ ██    ██ ███████ ██ ██      ███████ ██████  ██ ██      ██    ██      ████   
██   ██  ██  ██  ██   ██ ██ ██      ██   ██ ██   ██ ██ ██      ██    ██       ██    
██   ██   ████   ██   ██ ██ ███████ ██   ██ ██████  ██ ███████ ██    ██       ██                                                                                                                                                                                                                                                                                                      
*/
/*
 * Reassuring that a room wasnt really already reserved and the checks above in the other logical objects arent with bugs/flaws
 */
CREATE OR REPLACE FUNCTION fn_trg_check_room_availability() --TESTED
RETURNS TRIGGER AS $$
DECLARE
    _room_available BOOLEAN;
BEGIN
    -- Check if the room is available for the given dates
    SELECT NOT EXISTS (
        SELECT 1
        FROM "reserves.room_reservation" rr
        INNER JOIN "reserves.reservation" r ON rr.reservation_id = r.id
        WHERE rr.room_id = NEW.room_id
          AND r.status IN ('P', 'C') -- Only consider Pending or Confirmed reservations
          AND r.begin_date < (
              SELECT end_date
              FROM "reserves.reservation"
              WHERE id = NEW.reservation_id
          )
          AND r.end_date > (
              SELECT begin_date
              FROM "reserves.reservation"
              WHERE id = NEW.reservation_id
          )
    ) INTO _room_available;

    IF NOT _room_available THEN
        RAISE EXCEPTION 'Room id % is not available for the selected dates.', NEW.room_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


DROP TRIGGER IF EXISTS trg_check_room_availability ON "reserves.room_reservation";
CREATE TRIGGER trg_check_room_availability
BEFORE INSERT OR UPDATE ON "reserves.room_reservation"
FOR EACH ROW
EXECUTE FUNCTION fn_trg_check_room_availability();


/*
████████ ██████   ██████          ██    ██ ██████  ██████   █████  ████████ ███████         ██████   ██████   ██████  ███    ███         
   ██    ██   ██ ██               ██    ██ ██   ██ ██   ██ ██   ██    ██    ██              ██   ██ ██    ██ ██    ██ ████  ████         
   ██    ██████  ██   ███         ██    ██ ██████  ██   ██ ███████    ██    █████           ██████  ██    ██ ██    ██ ██ ████ ██         
   ██    ██   ██ ██    ██         ██    ██ ██      ██   ██ ██   ██    ██    ██              ██   ██ ██    ██ ██    ██ ██  ██  ██         
   ██    ██   ██  ██████  ███████  ██████  ██      ██████  ██   ██    ██    ███████ ███████ ██   ██  ██████   ██████  ██      ██ ███████ 
                                                                                                                                         
███████ ████████  █████  ████████ ██    ██ ███████          
██         ██    ██   ██    ██    ██    ██ ██               
███████    ██    ███████    ██    ██    ██ ███████         
     ██    ██    ██   ██    ██    ██    ██      ██          
███████    ██    ██   ██    ██     ██████  ███████ ███████ 
                                                                                                                                                                                                                                                                                                                       
*/
/*
 * Makes rooms related to a rejected or cancelled reservation available again
*/
CREATE OR REPLACE FUNCTION fn_trg_update_room_status_upon_cancelation() --WORKING --TESTED
RETURNS TRIGGER AS $$
BEGIN
    -- If the reservation is being rejected ('R') or cancelled ('CC'), mark the rooms as available
    IF NEW.status IN ('R', 'CC') THEN
        UPDATE "room_management.room"
        SET condition = 0 -- 0 indicates available
        WHERE id IN (
            SELECT room_id -- Associated rooms are updated in one operation within the trigger
            FROM "reserves.room_reservation"
            WHERE reservation_id = NEW.id
        );
    END IF;

    IF NEW.status IN ('C', 'P') THEN
        UPDATE "room_management.room"
        SET condition = 1 -- 1 indicates BEING USED
        WHERE id IN (
            SELECT room_id -- Associated rooms are updated in one operation within the trigger
            FROM "reserves.room_reservation"
            WHERE reservation_id = NEW.id
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_update_room_status_upon_cancelation ON "reserves.reservation";
CREATE TRIGGER trg_update_room_status_upon_cancelation
AFTER UPDATE OF status ON "reserves.reservation"
FOR EACH ROW
EXECUTE FUNCTION fn_trg_update_room_status_upon_cancelation();





/*
 ██████ ██   ██ ███████  ██████ ██   ██     ██ ███    ██        ██         ██████ ██   ██ ███████  ██████ ██   ██      ██████  ██    ██ ████████ 
██      ██   ██ ██      ██      ██  ██      ██ ████   ██        ██        ██      ██   ██ ██      ██      ██  ██      ██    ██ ██    ██    ██    
██      ███████ █████   ██      █████       ██ ██ ██  ██     ████████     ██      ███████ █████   ██      █████       ██    ██ ██    ██    ██    
██      ██   ██ ██      ██      ██  ██      ██ ██  ██ ██     ██  ██       ██      ██   ██ ██      ██      ██  ██      ██    ██ ██    ██    ██    
 ██████ ██   ██ ███████  ██████ ██   ██     ██ ██   ████     ██████        ██████ ██   ██ ███████  ██████ ██   ██      ██████   ██████     ██    
                                                                                                                                                 
*/




CREATE OR REPLACE PROCEDURE sp_check_in(reservation_id INT) --tested
LANGUAGE plpgsql
AS $$
BEGIN
    -- Ensure the reservation exists and is confirmed
    IF NOT EXISTS (
        SELECT 1 FROM "reserves.reservation"
        WHERE id = reservation_id AND status = 'C'
    ) THEN
        RAISE EXCEPTION 'Reservation % is not confirmed or does not exist.', reservation_id;
    END IF;

    -- Set the check-in timestamp
    UPDATE "reserves.reservation"
    SET status = 'CI'
    WHERE id = reservation_id;

    RAISE NOTICE 'Check-in completed for reservation id %.', reservation_id;
END;
$$;



CREATE OR REPLACE PROCEDURE sp_check_out(reservation_id INT) --tested
LANGUAGE plpgsql
AS $$
BEGIN
    -- Ensure the reservation exists and check-in has occurred
    IF NOT EXISTS (
        SELECT 1 FROM "reserves.reservation"
        WHERE id = reservation_id AND begin_date IS NOT NULL
    ) THEN
        RAISE EXCEPTION 'Reservation % has not been checked in or does not exist.', reservation_id;
    END IF;

    -- Set the check-out timestamp
    UPDATE "reserves.reservation"
    SET status = 'CO'
    WHERE id = reservation_id;

    RAISE NOTICE 'Check-out completed for reservation id %.', reservation_id;
END;
$$;





CREATE OR REPLACE FUNCTION fn_update_room_condition() --TESTED
RETURNS TRIGGER AS $$
BEGIN
    -- Update the room condition to "2" (e.g., cleaning or maintenance required)
    UPDATE "room_management.room"
    SET condition = 2 -- Assuming "2" represents cleaning or maintenance
    WHERE id IN (
        SELECT room_id
        FROM "reserves.room_reservation"
        WHERE reservation_id = OLD.id
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_update_room_condition ON "reserves.reservation";
CREATE TRIGGER trg_update_room_condition
AFTER UPDATE OF status ON "reserves.reservation"
FOR EACH ROW
WHEN (NEW.status = 'CO') -- Fire only when the status is set to 'CO' (Checked Out)
EXECUTE FUNCTION fn_update_room_condition();






