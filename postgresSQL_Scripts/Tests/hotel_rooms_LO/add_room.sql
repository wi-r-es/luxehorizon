CREATE OR REPLACE FUNCTION TEST_add_room(
    _hotel_id INT,
    _room_type_initials VARCHAR(100),
    _room_number INT,
    _base_price NUMERIC(10, 2),
    _condition INT DEFAULT 0
)
RETURNS TEXT AS $$
DECLARE
    room_exists BOOLEAN;
    hotel_exists BOOLEAN;
    room_type_exists BOOLEAN;
    result TEXT;
BEGIN
    -- Check if the hotel exists
    SELECT EXISTS (
        SELECT 1 
        FROM "management.hotel"
        WHERE id = _hotel_id
    ) INTO hotel_exists;

    IF NOT hotel_exists THEN
        RETURN 'NOK: Hotel does not exist';
    END IF;

    -- Check if the room type exists
    SELECT EXISTS (
        SELECT 1
        FROM "room_management.room_types"
        WHERE type_initials = _room_type_initials
    ) INTO room_type_exists;

    IF NOT room_type_exists THEN
        RETURN 'NOK: Room type does not exist';
    END IF;

    -- Call the procedure to add the room
    BEGIN
        CALL sp_add_room(
            _hotel_id, _room_type_initials, _room_number, _base_price, _condition
        );

        -- Verify the room insertion
        SELECT EXISTS (
            SELECT 1
            FROM "hotel_management.rooms"
            WHERE hotel = _hotel_id
              AND room_number = _room_number
        ) INTO room_exists;

        IF room_exists THEN
            result := 'OK';
        ELSE
            result := 'NOK: Room not added correctly';
        END IF;
    EXCEPTION WHEN OTHERS THEN
        result := 'NOK: Procedure failed - ' || SQLERRM;
    END;

    RETURN result;
END $$ LANGUAGE plpgsql;


--Test invocation
SELECT TEST_add_room(
    1, 
    'MPF', 
    101, 
    600.00, 
    0 
);
