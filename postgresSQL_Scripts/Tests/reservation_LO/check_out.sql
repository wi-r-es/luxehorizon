CREATE OR REPLACE FUNCTION TEST_check_out(
    _reservation_id INT
)
RETURNS TEXT AS $$
DECLARE
    reservation_status TEXT;
    result TEXT;
BEGIN
    -- Call the procedure to check out
    BEGIN
        CALL sp_check_out(_reservation_id);

        -- Verify the reservation status is updated
        SELECT status
        INTO reservation_status
        FROM "reserves.reservation"
        WHERE id = _reservation_id;

        IF reservation_status = 'CO' THEN
            result := 'OK';
        ELSE
            result := 'NOK: Check-out failed';
        END IF;
    EXCEPTION WHEN OTHERS THEN
        result := 'NOK: Procedure failed - ' || SQLERRM;
    END;

    RETURN result;
END $$ LANGUAGE plpgsql;

--Test invocation
SELECT TEST_check_out(1);