CREATE OR REPLACE FUNCTION TEST_change_password(
    _user_id INT,
    _new_hashed_password TEXT
)
RETURNS TEXT AS $$
DECLARE
    password_updated BOOLEAN;
    password_in_history BOOLEAN;
    result TEXT;
BEGIN
    -- Call the procedure to change the password
    BEGIN
        CALL sp_change_password(_user_id, _new_hashed_password);

        -- Verify the password in the users table
        SELECT EXISTS (
            SELECT 1
            FROM "hr.users"
            WHERE id = _user_id
              AND hashed_password = _new_hashed_password
        ) INTO password_updated;

        IF NOT password_updated THEN
            RETURN 'NOK: Password not updated in users table';
        END IF;

        -- Verify the password in the password history table
        SELECT EXISTS (
            SELECT 1
            FROM "sec.user_passwords_dictionary"
            WHERE user_id = _user_id
              AND hashed_password = _new_hashed_password
        ) INTO password_in_history;

        IF password_in_history THEN
            result := 'OK';
        ELSE
            result := 'NOK: Password not added to history';
        END IF;
    EXCEPTION WHEN OTHERS THEN
        result := 'NOK: Procedure failed - ' || SQLERRM;
    END;

    RETURN result;
END $$ LANGUAGE plpgsql;

--Test invocation
SELECT TEST_change_password(1, '1new_secure_hashed_password');





