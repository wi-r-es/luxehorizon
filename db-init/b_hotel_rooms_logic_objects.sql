/*
███████ ██████           █████  ██████  ██████          ██   ██  ██████  ████████ ███████ ██      
██      ██   ██         ██   ██ ██   ██ ██   ██         ██   ██ ██    ██    ██    ██      ██      
███████ ██████          ███████ ██   ██ ██   ██         ███████ ██    ██    ██    █████   ██      
     ██ ██              ██   ██ ██   ██ ██   ██         ██   ██ ██    ██    ██    ██      ██      
███████ ██      ███████ ██   ██ ██████  ██████  ███████ ██   ██  ██████     ██    ███████ ███████ 
                                                                                                  
*/
-- Procedure to add hotel
CREATE OR REPLACE PROCEDURE sp_add_hotel(
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
        INSERT INTO "management.hotel" (
            h_name, full_address, postal_code, city, email, telephone, details, stars
        ) VALUES (
            _name, _address, _postal_code, _city, _email, _telephone, _details, _stars
        );

        RAISE NOTICE 'Hotel % added successfully', _name;

    EXCEPTION WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS msg = MESSAGE_TEXT,
                                content = PG_EXCEPTION_DETAIL,
                                hint = PG_EXCEPTION_HINT;
        CALL sp_secLogError(msg, hint, content );

        RAISE NOTICE E'--- Call content ---\n%', content;
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
CREATE OR REPLACE PROCEDURE sp_add_room(
    _hotel_id INT,
    _room_type_initials VARCHAR(100),
    _room_number INT,
    _base_price NUMERIC(10, 2),
    _condition INT DEFAULT 0 -- Available = 0
)
LANGUAGE plpgsql
AS $$
DECLARE
    _hotel_exists BOOLEAN;
    _room_type_id INT;
    msg TEXT;
    content TEXT;
    hint TEXT;
BEGIN
    -- Validate room type exists
    SELECT id INTO _room_type_id
    FROM "room_management.room_types"
    WHERE type_initials = _room_type_initials;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Room type with initials % does not exist', _room_type_initials;
    END IF;

    SELECT EXISTS (
        SELECT 1 
        FROM "management.hotel"
        WHERE id = _hotel_id
    ) INTO _hotel_exists;

    IF NOT _hotel_exists THEN
        RAISE EXCEPTION 'Hotel id % does not exist', _hotel_id;
    END IF;
    BEGIN
        -- Insert new room
        INSERT INTO "hotel_management.rooms" (
            hotel,
            room_type,
            room_number,
            base_price,
            condition
        ) VALUES (
            _hotel_id,
            _room_type_id,
            _room_number,
            _base_price,
            _condition
        );

        RAISE NOTICE 'Room % added to Hotel id %', _room_number, _hotel_id;

    EXCEPTION WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS msg = MESSAGE_TEXT,
                                content = PG_EXCEPTION_DETAIL,
                                hint = PG_EXCEPTION_HINT;
        CALL sp_secLogError(msg, hint, content );

        RAISE NOTICE E'--- Call content ---\n%', content;
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
CREATE OR REPLACE PROCEDURE sp_update_room_status(
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
    SELECT EXISTS (
        SELECT 1 
        FROM "room_management.room" 
        WHERE id = _room_id
    ) INTO _room_exists;

    IF NOT _room_exists THEN
        RAISE EXCEPTION 'Room id % does not exist', _room_id;
    END IF;

    BEGIN
        UPDATE "room_management.room"
        SET condition = _new_status
        WHERE id = _room_id;

        RAISE NOTICE 'Room id % status updated to %', _room_id, _new_status;
    EXCEPTION WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS msg = MESSAGE_TEXT,
                                content = PG_EXCEPTION_DETAIL,
                                hint = PG_EXCEPTION_HINT;
        CALL sp_secLogError(msg, hint, content );

        RAISE NOTICE E'--- Call content ---\n%', content;
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

CREATE OR REPLACE PROCEDURE sp_link_commodity_to_room(
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
    SELECT EXISTS (
        SELECT 1 
        FROM "room_management.room" 
        WHERE id = _room_id
    ) INTO _room_exists;

    IF NOT _room_exists THEN
        RAISE EXCEPTION 'Room id % does not exist', _room_id;
    END IF;

    SELECT EXISTS (
        SELECT 1 
        FROM "room_management.commodity" 
        WHERE id = _commodity_id
    ) INTO _commodity_exists;

    IF NOT _commodity_exists THEN
        RAISE EXCEPTION 'Commodity id % does not exist', _commodity_id;
    END IF;

    BEGIN
        INSERT INTO "room_management.room_commodity" (room_id, commodity_id)
        VALUES (_room_id, _commodity_id);

        RAISE NOTICE 'Room id % linked to Commodity id %', _room_id, _commodity_id;
    EXCEPTION WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS msg = MESSAGE_TEXT,
                                content = PG_EXCEPTION_DETAIL,
                                hint = PG_EXCEPTION_HINT;
        CALL sp_secLogError(msg, hint, content );

        RAISE NOTICE E'--- Call content ---\n%', content;
    END;  
END;
$$;

/*
███████ ██████           ██████ ██████  ███████  █████  ████████ ███████          ██████  ██████  ███    ███ ███    ███  ██████  ██████  ██ ████████ ██    ██ 
██      ██   ██         ██      ██   ██ ██      ██   ██    ██    ██              ██      ██    ██ ████  ████ ████  ████ ██    ██ ██   ██ ██    ██     ██  ██  
███████ ██████          ██      ██████  █████   ███████    ██    █████           ██      ██    ██ ██ ████ ██ ██ ████ ██ ██    ██ ██   ██ ██    ██      ████   
     ██ ██              ██      ██   ██ ██      ██   ██    ██    ██              ██      ██    ██ ██  ██  ██ ██  ██  ██ ██    ██ ██   ██ ██    ██       ██    
███████ ██      ███████  ██████ ██   ██ ███████ ██   ██    ██    ███████ ███████  ██████  ██████  ██      ██ ██      ██  ██████  ██████  ██    ██       ██    
*/
CREATE OR REPLACE PROCEDURE sp_create_commodity(
    _commodity_detail VARCHAR(100)
)
LANGUAGE plpgsql
AS $$
DECLARE
    msg TEXT;
    content TEXT;
    hint TEXT;
BEGIN
    IF EXISTS (
        SELECT 1
        FROM "room_management.commodity"
        WHERE details = _commodity_detail
    ) THEN
        RAISE EXCEPTION 'Commodity % already exists.', _commodity_detail;
    END IF;
    BEGIN
        INSERT INTO "room_management.commodity" (details)
        VALUES (_commodity_detail);

        RAISE NOTICE 'Commodity % created successfully.', _commodity_detail;
    EXCEPTION WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS msg = MESSAGE_TEXT,
                                content = PG_EXCEPTION_DETAIL,
                                hint = PG_EXCEPTION_HINT;
        CALL sp_secLogError(msg, hint, content );

        RAISE NOTICE E'--- Call content ---\n%', content;
    END;  
END;
$$;





