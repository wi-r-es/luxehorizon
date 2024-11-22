/*
███████ ██████           █████  ██████  ██████          ██   ██  ██████  ████████ ███████ ██      
██      ██   ██         ██   ██ ██   ██ ██   ██         ██   ██ ██    ██    ██    ██      ██      
███████ ██████          ███████ ██   ██ ██   ██         ███████ ██    ██    ██    █████   ██      
     ██ ██              ██   ██ ██   ██ ██   ██         ██   ██ ██    ██    ██    ██      ██      
███████ ██      ███████ ██   ██ ██████  ██████  ███████ ██   ██  ██████     ██    ███████ ███████ 
                                                                                                  
*/
-- Procedure to add hotel
CREATE OR REPLACE PROCEDURE MANAGEMENT.sp_add_hotel(
    _name VARCHAR(100),
    _address VARCHAR(160),
    _postal_code VARCHAR(8),
    _city VARCHAR(100),
    _email VARCHAR(100),
    _telephone VARCHAR(20),
    _details VARCHAR(200),
    _stars INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    msg TEXT;
    content TEXT;
    hint TEXT;
BEGIN
    BEGIN
        INSERT INTO MANAGEMENT.HOTEL (
            H_NAME, FULL_ADDRESS, POSTAL_CODE, CITY, EMAIL, TELEPHONE, DETAILS, STARS
        ) VALUES (
            _name, _address, _postal_code, _city, _email, _telephone, _details, _stars
        );

        RAISE NOTICE 'Hotel % added successfully', _name;
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
███████ ██████           █████  ██████  ██████          ██████   ██████   ██████  ███    ███ 
██      ██   ██         ██   ██ ██   ██ ██   ██         ██   ██ ██    ██ ██    ██ ████  ████ 
███████ ██████          ███████ ██   ██ ██   ██         ██████  ██    ██ ██    ██ ██ ████ ██ 
     ██ ██              ██   ██ ██   ██ ██   ██         ██   ██ ██    ██ ██    ██ ██  ██  ██ 
███████ ██      ███████ ██   ██ ██████  ██████  ███████ ██   ██  ██████   ██████  ██      ██ 
                                                                                             
*/
-- Procedure to add room
CREATE OR REPLACE PROCEDURE ROOM_MANAGEMENT.sp_add_room(
    _hotel_id INT,
    _type_id INT,
    _room_number INT,
    _base_price NUMERIC(10, 2),
    _condition INT DEFAULT 0, -- Available = 0
    _capacity capacity_type
)
LANGUAGE plpgsql
AS $$
DECLARE
    _hotel_exists BOOLEAN;
    _type_exists BOOLEAN;
    msg TEXT;
    content TEXT;
    hint TEXT;
BEGIN
    -- Check if the hotel exists
    SELECT EXISTS (
        SELECT 1 
        FROM MANAGEMENT.HOTEL 
        WHERE ID = _hotel_id
    ) INTO _hotel_exists;

    IF NOT _hotel_exists THEN
        RAISE EXCEPTION 'Hotel ID % does not exist', _hotel_id;
    END IF;

    -- Check if the room type exists
    SELECT EXISTS (
        SELECT 1 
        FROM ROOM_MANAGEMENT.ROOM_TYPES 
        WHERE ID = _type_id
    ) INTO _type_exists;

    IF NOT _type_exists THEN
        RAISE EXCEPTION 'Room Type ID % does not exist', _type_id;
    END IF;

    BEGIN
        INSERT INTO ROOM_MANAGEMENT.ROOM (
            TYPE_ID, HOTEL_ID, ROOM_NUMBER, BASE_PRICE, CONDITION, CAPACITY
        ) VALUES (
            _type_id, _hotel_id, _room_number, _base_price, _condition, _capacity
        );

        RAISE NOTICE 'Room % added to Hotel ID %', _room_number, _hotel_id;
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
███████ ██████          ██    ██ ██████  ██████   █████  ████████ ███████         
██      ██   ██         ██    ██ ██   ██ ██   ██ ██   ██    ██    ██              
███████ ██████          ██    ██ ██████  ██   ██ ███████    ██    █████           
     ██ ██              ██    ██ ██      ██   ██ ██   ██    ██    ██              
███████ ██      ███████  ██████  ██      ██████  ██   ██    ██    ███████ ███████ 
                                                                                 
██████   ██████   ██████  ███    ███         ███████ ████████  █████  ████████ ██    ██ ███████ 
██   ██ ██    ██ ██    ██ ████  ████         ██         ██    ██   ██    ██    ██    ██ ██      
██████  ██    ██ ██    ██ ██ ████ ██         ███████    ██    ███████    ██    ██    ██ ███████ 
██   ██ ██    ██ ██    ██ ██  ██  ██              ██    ██    ██   ██    ██    ██    ██      ██ 
██   ██  ██████   ██████  ██      ██ ███████ ███████    ██    ██   ██    ██     ██████  ███████ 
                                                                                                
                                                                                                                                                                                
*/
CREATE OR REPLACE PROCEDURE ROOM_MANAGEMENT.sp_update_room_status(
    _room_id INT,
    _new_status INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    _room_exists BOOLEAN;
    msg TEXT;
    content TEXT;
    hint TEXT;
BEGIN
    -- Check if the room exists
    SELECT EXISTS (
        SELECT 1 
        FROM ROOM_MANAGEMENT.ROOM 
        WHERE ID = _room_id
    ) INTO _room_exists;

    IF NOT _room_exists THEN
        RAISE EXCEPTION 'Room ID % does not exist', _room_id;
    END IF;

    BEGIN
        UPDATE ROOM_MANAGEMENT.ROOM
        SET CONDITION = _new_status
        WHERE ID = _room_id;

        RAISE NOTICE 'Room ID % status updated to %', _room_id, _new_status;
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
███████ ██████          ██      ██ ███    ██ ██   ██          ██████  ██████  ███    ███ ███    ███  ██████  ██████  ██ ████████ ██    ██ 
██      ██   ██         ██      ██ ████   ██ ██  ██          ██      ██    ██ ████  ████ ████  ████ ██    ██ ██   ██ ██    ██     ██  ██  
███████ ██████          ██      ██ ██ ██  ██ █████           ██      ██    ██ ██ ████ ██ ██ ████ ██ ██    ██ ██   ██ ██    ██      ████   
     ██ ██              ██      ██ ██  ██ ██ ██  ██          ██      ██    ██ ██  ██  ██ ██  ██  ██ ██    ██ ██   ██ ██    ██       ██    
███████ ██      ███████ ███████ ██ ██   ████ ██   ██ ███████  ██████  ██████  ██      ██ ██      ██  ██████  ██████  ██    ██       ██    
                                                                                                                                          
████████  ██████          ██████   ██████   ██████  ███    ███ 
   ██    ██    ██         ██   ██ ██    ██ ██    ██ ████  ████ 
   ██    ██    ██         ██████  ██    ██ ██    ██ ██ ████ ██ 
   ██    ██    ██         ██   ██ ██    ██ ██    ██ ██  ██  ██ 
   ██     ██████  ███████ ██   ██  ██████   ██████  ██      ██ 
                                                               
                                                                    
*/

CREATE OR REPLACE PROCEDURE ROOM_MANAGEMENT.sp_link_commodity_to_room(
    _room_id INT,
    _commodity_id INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    _room_exists BOOLEAN;
    _commodity_exists BOOLEAN;
    msg TEXT;
    content TEXT;
    hint TEXT;
BEGIN
    -- Check if the room exists
    SELECT EXISTS (
        SELECT 1 
        FROM ROOM_MANAGEMENT.ROOM 
        WHERE ID = _room_id
    ) INTO _room_exists;

    IF NOT _room_exists THEN
        RAISE EXCEPTION 'Room ID % does not exist', _room_id;
    END IF;

    -- Check if the commodity exists
    SELECT EXISTS (
        SELECT 1 
        FROM ROOM_MANAGEMENT.COMMODITY 
        WHERE ID = _commodity_id
    ) INTO _commodity_exists;

    IF NOT _commodity_exists THEN
        RAISE EXCEPTION 'Commodity ID % does not exist', _commodity_id;
    END IF;

    BEGIN
        INSERT INTO ROOM_MANAGEMENT.ROOM_COMMODITY (ROOM_ID, COMMODITY_ID)
        VALUES (_room_id, _commodity_id);

        RAISE NOTICE 'Room ID % linked to Commodity ID %', _room_id, _commodity_id;
    EXCEPTION WHEN OTHERS THEN
        msg = MESSAGE_TEXT,
        content = PG_EXCEPTION_DETAIL,
        hint = PG_EXCEPTION_HINT;
            CALL SEC.LogError(msg, hint, content );
            RAISE;
    END;  
END;
$$;




