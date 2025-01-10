CREATE OR REPLACE FUNCTION TEST_update_room_status(
    _room_id INT,
    _new_status INT
)
RETURNS TEXT AS $$
DECLARE
    room_exists BOOLEAN;
    current_status INT;
    result TEXT;
BEGIN
    -- Check if the room exists
    SELECT EXISTS (
        SELECT 1 
        FROM "room_management.room"
        WHERE id = _room_id
    ) INTO room_exists;

    IF NOT room_exists THEN
        RETURN 'NOK: Room does not exist';
    END IF;

    -- Call the procedure to update the room status
    BEGIN
        CALL sp_update_room_status(_room_id, _new_status);

        -- Verify the update
        SELECT condition
        INTO current_status
        FROM "room_management.room"
        WHERE id = _room_id;

        IF current_status = _new_status THEN
            result := 'OK';
        ELSE
            result := 'NOK: Room status not updated correctly';
        END IF;
    EXCEPTION WHEN OTHERS THEN
        result := 'NOK: Procedure failed - ' || SQLERRM;
    END;

    RETURN result;
END $$ LANGUAGE plpgsql;

--Test invocation
SELECT TEST_update_room_status(1, 1); 
