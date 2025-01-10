CREATE OR REPLACE FUNCTION TEST_check_in(
    _reservation_id INT
)
RETURNS TEXT AS $$
DECLARE
    reservation_checked_in BOOLEAN;
    result TEXT;
BEGIN
    -- Call the function to check in
    BEGIN
        CALL sp_check_in(_reservation_id);

        -- Verify the check-in timestamp was set
        SELECT EXISTS (
            SELECT 1 
            FROM "reserves.reservation"
            WHERE id = _reservation_id
              AND begin_date::DATE = CURRENT_DATE
        ) INTO reservation_checked_in;

        IF reservation_checked_in THEN
            result := 'OK';
        ELSE
            result := 'NOK: Check-in failed';
        END IF;
    EXCEPTION WHEN OTHERS THEN
        result := 'NOK: Function failed - ' || SQLERRM;
    END;

    RETURN result;
END $$ LANGUAGE plpgsql;

--Test invocation
SELECT TEST_check_in(1); -- Check in for reservation with ID 1
