/*
 ██████  ███████ ████████         ███████ ███████  █████  ███████  ██████  ███    ██ 
██       ██         ██            ██      ██      ██   ██ ██      ██    ██ ████   ██ 
██   ███ █████      ██            ███████ █████   ███████ ███████ ██    ██ ██ ██  ██ 
██    ██ ██         ██                 ██ ██      ██   ██      ██ ██    ██ ██  ██ ██ 
 ██████  ███████    ██    ███████ ███████ ███████ ██   ██ ███████  ██████  ██   ████ 
                                                                                     
*/

/*
 * Determine the highest grossing season during the reservation period
 * Returns the highest grpossing season ID in the given period
 */

CREATE OR REPLACE FUNCTION FINANCE.fn_get_season(
    _begin_date DATE,
    _end_date DATE
) RETURNS INT AS $$
DECLARE
    _season_id INT;
BEGIN
    SELECT s.ID
    INTO _season_id
    FROM FINANCE.SEASON s
    INNER JOIN FINANCE.PRICE_PER_SEASON pps ON s.ID = pps.SEASON_ID
    WHERE s.BEGIN_DATE <= _end_date
      AND s.END_DATE >= _begin_date
    ORDER BY pps.TAX DESC
    LIMIT 1;

    IF NOT FOUND THEN
        RETURN NULL;
    END IF;

    RETURN _season_id;
END;
$$ LANGUAGE plpgsql;




/*
███████ ██████           ██████ ██████  ███████  █████  ████████ ███████         ██████  ███████ ███████ ███████ ██████  ██    ██  █████  ████████ ██  ██████  ███    ██ 
██      ██   ██         ██      ██   ██ ██      ██   ██    ██    ██              ██   ██ ██      ██      ██      ██   ██ ██    ██ ██   ██    ██    ██ ██    ██ ████   ██ 
███████ ██████          ██      ██████  █████   ███████    ██    █████           ██████  █████   ███████ █████   ██████  ██    ██ ███████    ██    ██ ██    ██ ██ ██  ██ 
     ██ ██              ██      ██   ██ ██      ██   ██    ██    ██              ██   ██ ██           ██ ██      ██   ██  ██  ██  ██   ██    ██    ██ ██    ██ ██  ██ ██ 
███████ ██      ███████  ██████ ██   ██ ███████ ██   ██    ██    ███████ ███████ ██   ██ ███████ ███████ ███████ ██   ██   ████   ██   ██    ██    ██  ██████  ██   ████ 
                                                                                                                                                                         
                                                                                                                                                                         
*/

CREATE OR REPLACE PROCEDURE RESERVES.sp_create_reservation(
    _client_id INT,
    _room_ids INT[],
    _begin_date DATE,
    _end_date DATE,
    OUT _reservation_id INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    _total_price NUMERIC(10, 2) := 0;
    _room_price NUMERIC(10, 2);
    _room_id INT;
    _room_available BOOLEAN;
    _season_id INT;
    msg TEXT;
    content TEXT;
    hint TEXT;
BEGIN
    -- Validate reservation dates
    IF _begin_date >= _end_date THEN
        RAISE EXCEPTION 'Begin date must be earlier than end date.';
    END IF;

    -- Calls function to get the season ID according to reservation dates 
    SELECT FINANCE.fn_get_season(_begin_date, _end_date)
    INTO _season_id;

    IF _season_id IS NULL THEN
        RAISE EXCEPTION 'No season found for the given dates.';
    END IF;

    -- Get the tax rate for the determined season
    SELECT TAX
    INTO _season_tax
    FROM FINANCE.PRICE_PER_SEASON
    WHERE SEASON_ID = _season_id;

    -- Check room availability and calculate total price
    FOR _room_id IN SELECT UNNEST(_room_ids) LOOP -- Expands an array into a set of rows
        SELECT BASE_PRICE 
        INTO _room_price
        FROM ROOM_MANAGEMENT.ROOM 
        WHERE ID = _room_id;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'Room ID % does not exist.', _room_id;
        END IF;

        -- Check if the room is already reserved
        SELECT NOT EXISTS (
            SELECT 1 
            FROM RESERVES.ROOM_RESERVATION rr
            INNER JOIN RESERVES.RESERVATION r ON rr.RESERVATION_ID = r.ID
            WHERE rr.ROOM_ID = _room_id
              AND r.BEGIN_DATE < _end_date
              AND r.END_DATE > _begin_date
        ) INTO _room_available;

        IF NOT _room_available THEN
            RAISE EXCEPTION 'Room ID % is not available for the selected dates.', _room_id;
        END IF;

         -- Calculate price with tax and add to total
        _room_price := _room_price + (_room_price * _season_tax); -- Season tax is already a float so its already 0.tax
        _total_price := _total_price + _room_price;
    END LOOP;
    BEGIN 

        INSERT INTO RESERVES.RESERVATION (
            CLIENT_ID, BEGIN_DATE, END_DATE, R_DETAIL, SEASON_ID, TOTAL_VALUE
        ) VALUES (
            _client_id, _begin_date, _end_date, 'P', _season_id, _total_price
        )
        RETURNING ID INTO _reservation_id;

        
        FOR _room_id IN SELECT UNNEST(_room_ids) LOOP
            INSERT INTO RESERVES.ROOM_RESERVATION (
                RESERVATION_ID, ROOM_ID, PRICE_RESERVATION
            ) VALUES (
                _reservation_id, _room_id, _room_price
            );
        END LOOP;

        RAISE NOTICE 'Reservation ID % created successfully for Client ID %', _reservation_id, _client_id;
    EXCEPTION WHEN OTHERS THEN
        msg = MESSAGE_TEXT,
        content = PG_EXCEPTION_DETAIL,
        hint = PG_EXCEPTION_HINT;
            CALL SEC.LogError(msg, hint, content );
            RAISE;
    END;    
END;
$$;


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
CREATE OR REPLACE PROCEDURE RESERVES.sp_update_reservation(
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
    msg TEXT;
    content TEXT;
    hint TEXT;
BEGIN
    -- Validate reservation dates
    IF _new_begin_date >= _new_end_date THEN
        RAISE EXCEPTION 'Begin date must be earlier than end date.';
    END IF;

    -- Check new room availability
    FOR _room_id IN SELECT UNNEST(_new_room_ids) LOOP -- Expands an array into a set of rows
        SELECT NOT EXISTS (
            SELECT 1 
            FROM RESERVES.ROOM_RESERVATION rr
            INNER JOIN RESERVES.RESERVATION r ON rr.RESERVATION_ID = r.ID
            WHERE rr.ROOM_ID = _room_id
              AND r.BEGIN_DATE < _new_end_date
              AND r.END_DATE > _new_begin_date
              AND r.ID <> _reservation_id
        ) INTO _room_available;

        IF NOT _room_available THEN
            RAISE EXCEPTION 'Room ID % is not available for the selected dates.', _room_id;
        END IF;
    END LOOP;
    BEGIN
        UPDATE RESERVES.RESERVATION
        SET BEGIN_DATE = _new_begin_date,
            END_DATE = _new_end_date
        WHERE ID = _reservation_id;
        
        --All existing room assignments for the reservation are removed
        DELETE FROM RESERVES.ROOM_RESERVATION WHERE RESERVATION_ID = _reservation_id;

        --Insert New Room Reservations
        FOR _room_id IN SELECT UNNEST(_new_room_ids) LOOP
            INSERT INTO ROOM_RESERVATION (
                RESERVATION_ID, ROOM_ID, PRICE_RESERVATION
            ) VALUES (
                _reservation_id, _room_id, (SELECT BASE_PRICE FROM ROOM WHERE ID = _room_id)
            );
        END LOOP;

        RAISE NOTICE 'Reservation ID % updated successfully.', _reservation_id;
    
    RAISE NOTICE 'Reservation ID % created successfully for Client ID %', _reservation_id, _client_id;
    EXCEPTION WHEN OTHERS THEN
        msg = MESSAGE_TEXT,
        content = PG_EXCEPTION_DETAIL,
        hint = PG_EXCEPTION_HINT;
            CALL SEC.LogError(msg, hint, content );
            RAISE;
    END;   
END;
$$;

/*
███████ ██████           ██████  █████  ███    ██  ██████ ███████ ██              ██████  ███████ ███████ ███████ ██████  ██    ██  █████  ████████ ██  ██████  ███    ██ 
██      ██   ██         ██      ██   ██ ████   ██ ██      ██      ██              ██   ██ ██      ██      ██      ██   ██ ██    ██ ██   ██    ██    ██ ██    ██ ████   ██ 
███████ ██████          ██      ███████ ██ ██  ██ ██      █████   ██              ██████  █████   ███████ █████   ██████  ██    ██ ███████    ██    ██ ██    ██ ██ ██  ██ 
     ██ ██              ██      ██   ██ ██  ██ ██ ██      ██      ██              ██   ██ ██           ██ ██      ██   ██  ██  ██  ██   ██    ██    ██ ██    ██ ██  ██ ██ 
███████ ██      ███████  ██████ ██   ██ ██   ████  ██████ ███████ ███████ ███████ ██   ██ ███████ ███████ ███████ ██   ██   ████   ██   ██    ██    ██  ██████  ██   ████ 
*/
CREATE OR REPLACE PROCEDURE RESERVES.sp_cancel_reservation(
    _reservation_id INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    msg TEXT;
    content TEXT;
    hint TEXT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM RESERVES.RESERVATION 
        WHERE ID = _reservation_id
    ) THEN
        RAISE EXCEPTION 'Reservation ID % does not exist.', _reservation_id;
    END IF;
    BEGIN 
        -- Delete room reservations
        DELETE FROM RESERVES.ROOM_RESERVATION
        WHERE RESERVATION_ID = _reservation_id;

        -- Update reservation status to "Cancelled"
        UPDATE RESERVES.RESERVATION
        SET R_DETAIL = 'CC' 
        WHERE ID = _reservation_id;

        RAISE NOTICE 'Reservation ID % cancelled successfully.', _reservation_id;

    RAISE NOTICE 'Reservation ID % created successfully for Client ID %', _reservation_id, _client_id;
    EXCEPTION WHEN OTHERS THEN
        msg = MESSAGE_TEXT,
        content = PG_EXCEPTION_DETAIL,
        hint = PG_EXCEPTION_HINT;
            CALL SEC.LogError(msg, hint, content );
            RAISE;
    END;   
END;
$$;

/*
███████ ██████           ██████  █████  ██       ██████ ██    ██ ██       █████  ████████ ███████         ██████  ██████  ██  ██████ ███████ 
██      ██   ██         ██      ██   ██ ██      ██      ██    ██ ██      ██   ██    ██    ██              ██   ██ ██   ██ ██ ██      ██      
███████ ██████          ██      ███████ ██      ██      ██    ██ ██      ███████    ██    █████           ██████  ██████  ██ ██      █████   
     ██ ██              ██      ██   ██ ██      ██      ██    ██ ██      ██   ██    ██    ██              ██      ██   ██ ██ ██      ██      
███████ ██      ███████  ██████ ██   ██ ███████  ██████  ██████  ███████ ██   ██    ██    ███████ ███████ ██      ██   ██ ██  ██████ ███████ 
                                                                                                                                             
                                                                                                                                             
*/

/*
 * Returns the price of a given room to a given season, TO BE USED WITH THE FRONTEND MAINLY
 */
CREATE OR REPLACE FUNCTION RESERVES.sp_calculate_price(
    _room_id INT,
    _season_id INT
) RETURNS NUMERIC(10, 2) AS $$
DECLARE
    _base_price NUMERIC(10, 2);
    _tax_rate FLOAT;
    _total_price NUMERIC(10, 2);
BEGIN
    SELECT BASE_PRICE INTO _base_price FROM ROOM_MANAGEMENT.ROOM WHERE ID = _room_id;

    SELECT TAX INTO _tax_rate FROM FINANCE.PRICE_PER_SEASON WHERE SEASON_ID = _season_id;

    _total_price := _base_price + (_base_price * _tax_rate );

    RETURN _total_price;
END;
$$ LANGUAGE plpgsql;

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
CREATE OR REPLACE FUNCTION RESERVES.trg_check_room_availability()
RETURNS TRIGGER AS $$
DECLARE
    _room_available BOOLEAN;
BEGIN
    SELECT NOT EXISTS (
        SELECT 1 
        FROM RESERVES.ROOM_RESERVATION rr
        INNER JOIN RESERVES.RESERVATION r ON rr.RESERVATION_ID = r.ID
        WHERE rr.ROOM_ID = NEW.ROOM_ID
          AND r.BEGIN_DATE < NEW.END_DATE
          AND r.END_DATE > NEW.BEGIN_DATE
    ) INTO _room_available;

    IF NOT _room_available THEN
        RAISE EXCEPTION 'Room ID % is not available for the selected dates.', NEW.ROOM_ID;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_room_availability
BEFORE INSERT OR UPDATE ON RESERVES.ROOM_RESERVATION
FOR EACH ROW
EXECUTE FUNCTION RESERVES.trg_check_room_availability();


/*
████████ ██████   ██████          ██    ██ ██████  ██████   █████  ████████ ███████         ██████   ██████   ██████  ███    ███         
   ██    ██   ██ ██               ██    ██ ██   ██ ██   ██ ██   ██    ██    ██              ██   ██ ██    ██ ██    ██ ████  ████         
   ██    ██████  ██   ███         ██    ██ ██████  ██   ██ ███████    ██    █████           ██████  ██    ██ ██    ██ ██ ████ ██         
   ██    ██   ██ ██    ██         ██    ██ ██      ██   ██ ██   ██    ██    ██              ██   ██ ██    ██ ██    ██ ██  ██  ██         
   ██    ██   ██  ██████  ███████  ██████  ██      ██████  ██   ██    ██    ███████ ███████ ██   ██  ██████   ██████  ██      ██ ███████ 
                                                                                                                                         
███████ ████████  █████  ████████ ██    ██ ███████          ██████  ███    ██         ██████  ███████ ███████ ███████ ██████  ██    ██  █████  ████████ ██  ██████  ███    ██ 
██         ██    ██   ██    ██    ██    ██ ██              ██    ██ ████   ██         ██   ██ ██      ██      ██      ██   ██ ██    ██ ██   ██    ██    ██ ██    ██ ████   ██ 
███████    ██    ███████    ██    ██    ██ ███████         ██    ██ ██ ██  ██         ██████  █████   ███████ █████   ██████  ██    ██ ███████    ██    ██ ██    ██ ██ ██  ██ 
     ██    ██    ██   ██    ██    ██    ██      ██         ██    ██ ██  ██ ██         ██   ██ ██           ██ ██      ██   ██  ██  ██  ██   ██    ██    ██ ██    ██ ██  ██ ██ 
███████    ██    ██   ██    ██     ██████  ███████ ███████  ██████  ██   ████ ███████ ██   ██ ███████ ███████ ███████ ██   ██   ████   ██   ██    ██    ██  ██████  ██   ████ 
                                                                                                                                                                                                                                                                                                                       
*/
/*
 * Makes rooms related to a rejected or cancelled reservation available again
*/
CREATE OR REPLACE FUNCTION RESERVES.trg_update_room_status_on_reservation()
RETURNS TRIGGER AS $$
BEGIN
    -- If the reservation is being rejected ('R') or cancelled ('CC'), mark the rooms as available
    IF NEW.R_DETAIL IN ('R', 'CC') THEN
        UPDATE ROOM_MANAGEMENT.ROOM
        SET CONDITION = 0 -- 0 indicates available
        WHERE ID IN (
            SELECT ROOM_ID -- Associated rooms are updated in one operation within the trigger
            FROM RESERVES.ROOM_RESERVATION
            WHERE RESERVATION_ID = NEW.ID
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER trg_update_room_status_on_reservation
AFTER UPDATE OF R_DETAIL ON RESERVES.RESERVATION
FOR EACH ROW
EXECUTE FUNCTION RESERVES.trg_update_room_status_on_reservation();



