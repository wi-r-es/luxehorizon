CREATE OR REPLACE FUNCTION TEST_create_commodity(
    _commodity_detail VARCHAR(100)
)
RETURNS TEXT AS $$
DECLARE
    commodity_exists BOOLEAN;
    result TEXT;
BEGIN
    -- Check if the commodity already exists
    SELECT EXISTS (
        SELECT 1
        FROM "room_management.commodity"
        WHERE details = _commodity_detail
    ) INTO commodity_exists;

    IF commodity_exists THEN
        RETURN 'NOK: Commodity already exists';
    END IF;

    -- Call the procedure to create the commodity
    BEGIN
        CALL sp_create_commodity(_commodity_detail);

        -- Verify the commodity insertion
        SELECT EXISTS (
            SELECT 1
            FROM "room_management.commodity"
            WHERE details = _commodity_detail
        ) INTO commodity_exists;

        IF commodity_exists THEN
            result := 'OK';
        ELSE
            result := 'NOK: Commodity not created correctly';
        END IF;
    EXCEPTION WHEN OTHERS THEN
        result := 'NOK: Procedure failed - ' || SQLERRM;
    END;

    RETURN result;
END $$ LANGUAGE plpgsql;

--Test invocation
SELECT TEST_create_commodity('Free WiFi');
