CREATE OR REPLACE FUNCTION TEST_link_commodity_to_room(
    _room_id INT,
    _commodity_id INT
)
RETURNS TEXT AS $$
DECLARE
    room_exists BOOLEAN;
    commodity_exists BOOLEAN;
    link_exists BOOLEAN;
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

    -- Check if the commodity exists
    SELECT EXISTS (
        SELECT 1 
        FROM "room_management.commodity"
        WHERE id = _commodity_id
    ) INTO commodity_exists;

    IF NOT commodity_exists THEN
        RETURN 'NOK: Commodity does not exist';
    END IF;

    -- Call the procedure to link the commodity to the room
    BEGIN
        CALL sp_link_commodity_to_room(_room_id, _commodity_id);

        -- Verify the link
        SELECT EXISTS (
            SELECT 1
            FROM "room_management.room_commodity"
            WHERE room_id = _room_id AND commodity_id = _commodity_id
        ) INTO link_exists;

        IF link_exists THEN
            result := 'OK';
        ELSE
            result := 'NOK: Link not created correctly';
        END IF;
    EXCEPTION WHEN OTHERS THEN
        result := 'NOK: Procedure failed - ' || SQLERRM;
    END;

    RETURN result;
END $$ LANGUAGE plpgsql;

--Test invocation
SELECT TEST_link_commodity_to_room(1, 1);


