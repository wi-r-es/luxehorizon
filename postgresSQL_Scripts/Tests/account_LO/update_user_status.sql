CREATE OR REPLACE FUNCTION TEST_update_user_status(
    _user_id INT,
    _is_active BOOLEAN
)
RETURNS TEXT AS $$
DECLARE
    current_status BOOLEAN;
    user_exists BOOLEAN;
    result TEXT;
BEGIN
    -- Call the procedure to update the user's status
    BEGIN
        CALL sp_update_user_status(_user_id, _is_active);

        -- Verify the update
        SELECT is_active
        INTO current_status
        FROM "hr.users"
        WHERE id = _user_id;

        IF current_status = _is_active THEN
            result := 'OK';
        ELSE
            result := 'NOK: User status not updated correctly';
        END IF;
    EXCEPTION WHEN OTHERS THEN
        result := 'NOK: Procedure failed - ' || SQLERRM;
    END;

    RETURN result;
END $$ LANGUAGE plpgsql;


--Test invocation
SELECT TEST_update_user_status(2, FALSE);