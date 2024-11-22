CREATE OR REPLACE PROCEDURE SEC.LogError(
    _ErrorMessage VARCHAR(4000),
    _ErrorHint VARCHAR(400),
    _ErrorContent VARCHAR(400)
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Log the error details into the error log table
    INSERT INTO SEC.ERROR_LOG (ERROR_MESSAGE, ERROR_HINT, ERROR_CONTENT)
    VALUES (_ErrorMessage, _ErrorHint, _ErrorContent);

    -- Raise the error to the caller
    RAISE EXCEPTION '%', _ErrorMessage
        USING ERRCODE = 'P0001', -- PostgreSQL user-defined exception code
              DETAIL = 'Error Hint: ' || _ErrorHint || ', Error Content: ' || _ErrorContent;
END;
$$;


CREATE OR REPLACE FUNCTION SEC.trg_insert_user_password_dictionary()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO SEC.USER_PASSWORDS_DICTIONARY (
        USER_ID, 
        HASHED_PASSWD, 
        ValidFrom, 
        ValidTo
    ) VALUES (
        NEW.ID, 
        NEW.HASHED_PASSWORD, 
        CURRENT_TIMESTAMP, 
        CASE 
            WHEN NEW.UTP = 'F' THEN CURRENT_TIMESTAMP + INTERVAL '6 months' -- Employees only
            ELSE CURRENT_TIMESTAMP + INTERVAL '100 years' 
        END
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER SEC.trg_after_user_insert_update
AFTER INSERT OR UPDATE OF HASHED_PASSWORD
ON HR.USERS
FOR EACH ROW
EXECUTE FUNCTION SEC.trg_insert_user_password_dictionary();


-- Log user login
CREATE OR REPLACE FUNCTION SEC.trg_track_user_login()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO SEC.USER_LOGIN_AUDIT (
        USER_ID, LOGIN_TIMESTAMP
    ) VALUES (
        NEW.ID, CURRENT_TIMESTAMP
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER SEC.trg_track_user_login
AFTER INSERT OR UPDATE ON USERS
FOR EACH ROW
WHEN (NEW.UTP = 'F') -- Optional: for employees only
EXECUTE FUNCTION SEC.trg_track_user_login();


-- IMPLEMENTATION OF HISTORY VERSIONING TABLE FROM MSSQL BUT FOR POSTEGRESQL 
CREATE OR REPLACE PROCEDURE SEC.sp_change_password(
    _user_id INT,
    _new_hashed_password TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    _is_password_reused BOOLEAN;
BEGIN
    -- Check if the new password has already been used by the user
    SELECT EXISTS (
        SELECT 1
        FROM SEC.USER_PASSWORDS_DICTIONARY
        WHERE USER_ID = _user_id
          AND HASHED_PASSWD = _new_hashed_password
    ) INTO _is_password_reused;

    -- If the password is already used, raise an exception
    IF _is_password_reused THEN
        RAISE EXCEPTION 'The new password has already been used by this user. Please choose a different password.';
    END IF;

    BEGIN 
        UPDATE HR.USERS
        SET HASHED_PASSWORD = _new_hashed_password
        WHERE ID = _user_id;

        -- Insert the new password into the password history table
        INSERT INTO SEC.USER_PASSWORDS_DICTIONARY (
            USER_ID, HASHED_PASSWD, ValidFrom, ValidTo
        ) VALUES (
            _user_id, 
            _new_hashed_password, 
            CURRENT_TIMESTAMP, 
            CASE 
                WHEN (SELECT UTP FROM HR.USERS WHERE ID = _user_id) = 'F' 
                THEN CURRENT_TIMESTAMP + INTERVAL '6 months' 
                ELSE CURRENT_TIMESTAMP + INTERVAL '100 years'
            END
        );

            RAISE NOTICE 'Password for User ID % changed successfully.', _user_id;
    EXCEPTION WHEN OTHERS THEN
        msg = MESSAGE_TEXT,
        content = PG_EXCEPTION_DETAIL,
        hint = PG_EXCEPTION_HINT;
            CALL SEC.LogError(msg, hint, content );

            RAISE;
    END;    
END;
$$;


