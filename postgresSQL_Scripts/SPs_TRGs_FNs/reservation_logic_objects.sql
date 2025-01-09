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

CREATE OR REPLACE FUNCTION fn_get_season(
    _begin_date DATE,
    _end_date DATE
) RETURNS INT AS $$
DECLARE
    _season_id INT;
BEGIN
    SELECT s.ID
    INTO _season_id
    FROM "FINANCE.SEASON" s
    INNER JOIN "FINANCE.PRICE_PER_SEASON" pps ON s.ID = pps.SEASON_ID
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

/* A FUNCIONAR  A FUNCIONAR A FUNCIONAR A FUNCIONAR A FUNCIONAR A FUNCIONAR A FUNCIONAR A FUNCIONAR A FUNCIONAR A FUNCIONAR A FUNCIONAR*/

CREATE OR REPLACE PROCEDURE create_reservation(
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
    season_id INTEGER;
    room_base_price NUMERIC;
	season_rate NUMERIC;
BEGIN
    -- Verificar se o quarto existe
    IF NOT EXISTS (SELECT 1 FROM "room_management.room" WHERE id = room_id) THEN
        RAISE EXCEPTION 'Quarto não encontrado.';
    END IF;

    -- Calcular número de noites
    nights := checkout - checkin;

    IF nights <= 0 THEN
        RAISE EXCEPTION 'As datas de check-in e check-out são inválidas.';
    END IF;

    -- Buscar temporada válida
    SELECT id, rate INTO season_id, season_rate
    FROM "finance.season"
    WHERE begin_date <= checkin AND end_date >= checkout;

    IF season_id IS NULL THEN
        RAISE EXCEPTION 'Sem temporada válida para as datas selecionadas.';
    END IF;

    -- Obter preço base do quarto
    SELECT base_price INTO room_base_price
    FROM "room_management.room"
    WHERE id = room_id;

    IF room_base_price IS NULL THEN
        RAISE EXCEPTION 'O quarto não possui preço definido.';
    END IF;

    -- Calcular preço total
    total_price := nights * room_base_price * season_rate;

    -- Inserir a reserva
    INSERT INTO "reserves.reservation" (client_id, begin_date, end_date, status, season_id, total_value)
    VALUES (user_id, checkin, checkout, 'P', season_id, total_price)
    RETURNING id INTO reservation_id;

    -- Relacionar o quarto à reserva
    INSERT INTO "reserves.room_reservation" (reservation_id, room_id, price_reservation)
    VALUES (reservation_id, room_id, total_price);

    -- Confirmação de sucesso
    RAISE NOTICE 'Reserva criada com sucesso. ID da reserva: %', reservation_id;
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
CREATE OR REPLACE PROCEDURE sp_update_reservation(
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
            FROM "RESERVES.ROOM_RESERVATION" rr
            INNER JOIN "RESERVES.RESERVATION" r ON rr.RESERVATION_ID = r.ID
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
        UPDATE "RESERVES.RESERVATION"
        SET BEGIN_DATE = _new_begin_date,
            END_DATE = _new_end_date
        WHERE ID = _reservation_id;
        
        --All existing room assignments for the reservation are removed
        DELETE FROM "RESERVES.ROOM_RESERVATION" WHERE RESERVATION_ID = _reservation_id;

        --Insert New Room Reservations
        FOR _room_id IN SELECT UNNEST(_new_room_ids) LOOP
            INSERT INTO "RESERVES.ROOM_RESERVATION" (
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
            CALL "SEC.LogError"(msg, hint, content );
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

/*
 * Cancel a reservation
 */
 
CREATE OR REPLACE PROCEDURE sp_cancel_reservation(
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
        RAISE EXCEPTION 'Reservation ID % does not exist.', _reservation_id;
    END IF;

    -- Deletar associações com quartos
    DELETE FROM "reserves.room_reservation"
    WHERE reservation_id = _reservation_id;

    -- Atualizar o status da reserva para "Cancelado"
    UPDATE "reserves.reservation"
    SET status = 'C'  -- Substituir 'C' pelo código adequado se necessário
    WHERE id = _reservation_id;

    -- Mensagem de sucesso
    RAISE NOTICE 'Reservation ID % cancelled successfully.', _reservation_id;

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
CREATE OR REPLACE FUNCTION fn_trg_check_room_availability()
RETURNS TRIGGER AS $$
DECLARE
    _room_available BOOLEAN;
BEGIN
    SELECT NOT EXISTS (
        SELECT 1 
        FROM "RESERVES.ROOM_RESERVATION" rr
        INNER JOIN "RESERVES.RESERVATION" r ON rr.RESERVATION_ID = r.ID
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
DROP TRIGGER IF EXISTS trg_check_room_availability ON "RESERVES.ROOM_RESERVATION";
CREATE TRIGGER trg_check_room_availability
BEFORE INSERT OR UPDATE ON "RESERVES.ROOM_RESERVATION"
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
CREATE OR REPLACE FUNCTION fn_trg_update_room_status_upon_cancelation()
RETURNS TRIGGER AS $$
BEGIN
    -- If the reservation is being rejected ('R') or cancelled ('CC'), mark the rooms as available
    IF NEW.status IN ('R', 'CC') THEN
        UPDATE "ROOM_MANAGEMENT.ROOM"
        SET CONDITION = 0 -- 0 indicates available
        WHERE ID IN (
            SELECT ROOM_ID -- Associated rooms are updated in one operation within the trigger
            FROM "RESERVES.ROOM_RESERVATION"
            WHERE RESERVATION_ID = NEW.ID
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_update_room_status_upon_cancelation ON "RESERVES.RESERVATION";
CREATE TRIGGER trg_update_room_status_upon_cancelation
AFTER UPDATE OF status ON "RESERVES.RESERVATION"
FOR EACH ROW
EXECUTE FUNCTION fn_trg_update_room_status_upon_cancelation();





CREATE OR REPLACE FUNCTION sp_check_in(RESERVATION_ID INT)
RETURNS VOID AS $$
BEGIN
    -- Ensure the reservation exists and is confirmed
    IF NOT EXISTS (
        SELECT 1 FROM "RESERVES.RESERVATION"
        WHERE ID = RESERVATION_ID AND status = 'C'
    ) THEN
        RAISE EXCEPTION 'Reservation % is not confirmed or does not exist.', RESERVATION_ID;
    END IF;

    -- Ensure the current date is within the reservation period
    IF NOT EXISTS (
        SELECT 1 FROM "RESERVES.RESERVATION"
        WHERE ID = RESERVATION_ID
          AND CURRENT_DATE BETWEEN BEGIN_DATE AND END_DATE
    ) THEN
        RAISE EXCEPTION 'Current date is not within the reservation period for reservation %.', RESERVATION_ID;
    END IF;

    -- Set the check-in timestamp
    UPDATE "RESERVES.RESERVATION"
    SET begin_date = CURRENT_TIMESTAMP
    WHERE ID = RESERVATION_ID;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION sp_check_out(RESERVATION_ID INT)
RETURNS VOID AS $$
BEGIN
    -- Ensure the reservation exists and check-in has occurred
    IF NOT EXISTS (
        SELECT 1 FROM "RESERVES.RESERVATION"
        WHERE ID = RESERVATION_ID AND begin_date IS NOT NULL
    ) THEN
        RAISE EXCEPTION 'Reservation % has not been checked in or does not exist.', RESERVATION_ID;
    END IF;

    -- Set the check-out timestamp
    UPDATE "RESERVES.RESERVATION"
    SET end_date = CURRENT_TIMESTAMP
    WHERE ID = RESERVATION_ID;
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION fn_update_room_condition()
RETURNS TRIGGER AS $$
BEGIN
    -- Update the room condition to "2" (e.g., cleaning or "3" - maintenance required)
    UPDATE "ROOM_MANAGEMENT.ROOM"
    SET CONDITION = 2
    WHERE ID IN (
        SELECT ROOM_ID
        FROM "RESERVES.ROOM_RESERVATION"
        WHERE RESERVATION_ID = OLD.ID
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_update_room_condition ON "RESERVES.RESERVATION";
CREATE TRIGGER trg_update_room_condition
AFTER UPDATE OF end_date ON "RESERVES.RESERVATION"
FOR EACH ROW
WHEN (OLD.end_date IS NULL AND NEW.end_date IS NOT NULL) -- Only fire on the first check-out update
EXECUTE FUNCTION fn_update_room_condition();





