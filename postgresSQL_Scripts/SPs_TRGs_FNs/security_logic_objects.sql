/*
██       ██████   ██████  ███████ ██████  ██████   ██████  ██████  
██      ██    ██ ██       ██      ██   ██ ██   ██ ██    ██ ██   ██ 
██      ██    ██ ██   ███ █████   ██████  ██████  ██    ██ ██████  
██      ██    ██ ██    ██ ██      ██   ██ ██   ██ ██    ██ ██   ██ 
███████  ██████   ██████  ███████ ██   ██ ██   ██  ██████  ██   ██                                                                    
*/
CREATE OR REPLACE PROCEDURE sp_secLogError(
    _ErrorMessage VARCHAR(4000),
    _ErrorHint VARCHAR(400),
    _ErrorContent VARCHAR(400)
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Log the error details into the error log table
    INSERT INTO "sec.error_log" (error_message, error_hint, error_context)
    VALUES (_ErrorMessage, _ErrorHint, _ErrorContent);

    -- Raise the error to the caller
    RAISE EXCEPTION '%', _ErrorMessage
        USING ERRCODE = 'P0001', -- PostgreSQL user-defined exception code
              DETAIL = 'Error Hint: ' || _ErrorHint || ', Error Content: ' || _ErrorContent;
END;
$$;

/*
████████ ██████   ██████          ██ ███    ██ ███████ ███████ ██████  ████████         ██    ██ ███████ ███████ ██████          
   ██    ██   ██ ██               ██ ████   ██ ██      ██      ██   ██    ██            ██    ██ ██      ██      ██   ██         
   ██    ██████  ██   ███         ██ ██ ██  ██ ███████ █████   ██████     ██            ██    ██ ███████ █████   ██████          
   ██    ██   ██ ██    ██         ██ ██  ██ ██      ██ ██      ██   ██    ██            ██    ██      ██ ██      ██   ██         
   ██    ██   ██  ██████  ███████ ██ ██   ████ ███████ ███████ ██   ██    ██    ███████  ██████  ███████ ███████ ██   ██ ███████

██████   █████  ███████ ███████ ██     ██  ██████  ██████  ██████          ██████  ██  ██████ ████████ ██  ██████  ███    ██  █████  ██████  ██    ██ 
██   ██ ██   ██ ██      ██      ██     ██ ██    ██ ██   ██ ██   ██         ██   ██ ██ ██         ██    ██ ██    ██ ████   ██ ██   ██ ██   ██  ██  ██  
██████  ███████ ███████ ███████ ██  █  ██ ██    ██ ██████  ██   ██         ██   ██ ██ ██         ██    ██ ██    ██ ██ ██  ██ ███████ ██████    ████   
██      ██   ██      ██      ██ ██ ███ ██ ██    ██ ██   ██ ██   ██         ██   ██ ██ ██         ██    ██ ██    ██ ██  ██ ██ ██   ██ ██   ██    ██    
██      ██   ██ ███████ ███████  ███ ███   ██████  ██   ██ ██████  ███████ ██████  ██  ██████    ██    ██  ██████  ██   ████ ██   ██ ██   ██    ██    
                                                                                                                                                         
*/
CREATE OR REPLACE FUNCTION trg_insert_user_password_dictionary()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO "SEC.USER_PASSWORDS_DICTIONARY" (
        user_id, 
        hashed_password, 
        valid_from, 
        valid_to
    ) VALUES (
        NEW.ID, 
        NEW.hashed_password, 
        CURRENT_TIMESTAMP, 
        CASE 
            WHEN NEW.utp = 'F' THEN CURRENT_TIMESTAMP + INTERVAL '6 months' -- Employees only
            ELSE CURRENT_TIMESTAMP + INTERVAL '100 years' 
        END
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_after_user_insert_update ON "HR.USERS";
CREATE TRIGGER trg_after_user_insert_update
AFTER INSERT OR UPDATE OF hashed_password
ON "HR.USERS"
FOR EACH ROW
EXECUTE FUNCTION trg_insert_user_password_dictionary();

/*
████████ ██████   ██████          ████████ ██████   █████   ██████ ██   ██         ██    ██ ███████ ███████ ██████          ██       ██████   ██████  ██ ███    ██ 
   ██    ██   ██ ██                  ██    ██   ██ ██   ██ ██      ██  ██          ██    ██ ██      ██      ██   ██         ██      ██    ██ ██       ██ ████   ██ 
   ██    ██████  ██   ███            ██    ██████  ███████ ██      █████           ██    ██ ███████ █████   ██████          ██      ██    ██ ██   ███ ██ ██ ██  ██ 
   ██    ██   ██ ██    ██            ██    ██   ██ ██   ██ ██      ██  ██          ██    ██      ██ ██      ██   ██         ██      ██    ██ ██    ██ ██ ██  ██ ██ 
   ██    ██   ██  ██████  ███████    ██    ██   ██ ██   ██  ██████ ██   ██ ███████  ██████  ███████ ███████ ██   ██ ███████ ███████  ██████   ██████  ██ ██   ████ 
                                                                                                                                                                   
*/
-- Log user login
CREATE OR REPLACE FUNCTION fn_track_user_login()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO "SEC.USER_LOGIN_AUDIT" (
        user_id, login_timestamp
    ) VALUES (
        NEW.ID, CURRENT_TIMESTAMP
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_track_user_login ON "HR.USERS";
CREATE TRIGGER trg_track_user_login
AFTER INSERT OR UPDATE ON "HR.USERS"
FOR EACH ROW
WHEN (NEW.utp = 'F') -- Optional: for employees only
EXECUTE FUNCTION fn_track_user_login();

/*
███████ ██████           ██████ ██   ██  █████  ███    ██  ██████  ███████         ██████   █████  ███████ ███████ ██     ██  ██████  ██████  ██████  
██      ██   ██         ██      ██   ██ ██   ██ ████   ██ ██       ██              ██   ██ ██   ██ ██      ██      ██     ██ ██    ██ ██   ██ ██   ██ 
███████ ██████          ██      ███████ ███████ ██ ██  ██ ██   ███ █████           ██████  ███████ ███████ ███████ ██  █  ██ ██    ██ ██████  ██   ██ 
     ██ ██              ██      ██   ██ ██   ██ ██  ██ ██ ██    ██ ██              ██      ██   ██      ██      ██ ██ ███ ██ ██    ██ ██   ██ ██   ██ 
███████ ██      ███████  ██████ ██   ██ ██   ██ ██   ████  ██████  ███████ ███████ ██      ██   ██ ███████ ███████  ███ ███   ██████  ██   ██ ██████  
                                                                                                                                                      
*/
-- IMPLEMENTATION OF HISTORY VERSIONING TABLE FROM MSSQL BUT FOR POSTEGRESQL 
CREATE OR REPLACE PROCEDURE sp_change_password(
    _user_id INT,
    _new_hashed_password TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    _is_password_reused BOOLEAN;
    msg text;
    hint text;
    content text;
BEGIN
    -- Check if the new password has already been used by the user
    SELECT EXISTS (
        SELECT 1
        FROM "SEC.USER_PASSWORDS_DICTIONARY"
        WHERE user_id = _user_id
          AND hashed_password = _new_hashed_password
    ) INTO _is_password_reused;

    -- If the password is already used, raise an exception
    IF _is_password_reused THEN
        RAISE EXCEPTION 'The new password has already been used by this user. Please choose a different password.';
    END IF;

    BEGIN 
        UPDATE "HR.USERS"
        SET hashed_password = _new_hashed_password
        WHERE ID = _user_id;

        -- Insert the new password into the password history table
        INSERT INTO "SEC.USER_PASSWORDS_DICTIONARY" (
            user_id, hashed_password, valid_from, valid_to
        ) VALUES (
            _user_id, 
            _new_hashed_password, 
            CURRENT_TIMESTAMP, 
            CASE 
                WHEN (SELECT utp FROM HR.USERS WHERE ID = _user_id) = 'F' 
                THEN CURRENT_TIMESTAMP + INTERVAL '6 months' 
                ELSE CURRENT_TIMESTAMP + INTERVAL '100 years'
            END
        );

            RAISE NOTICE 'Password for User ID % changed successfully.', _user_id;
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
████████ ██████   ██████          ██       ██████   ██████           ██████ ██   ██  █████  ███    ██  ██████  ███████ ███████ 
   ██    ██   ██ ██               ██      ██    ██ ██               ██      ██   ██ ██   ██ ████   ██ ██       ██      ██      
   ██    ██████  ██   ███         ██      ██    ██ ██   ███         ██      ███████ ███████ ██ ██  ██ ██   ███ █████   ███████ 
   ██    ██   ██ ██    ██         ██      ██    ██ ██    ██         ██      ██   ██ ██   ██ ██  ██ ██ ██    ██ ██           ██ 
   ██    ██   ██  ██████  ███████ ███████  ██████   ██████  ███████  ██████ ██   ██ ██   ██ ██   ████  ██████  ███████ ███████ 
                                                                                                                               
*/
CREATE OR REPLACE FUNCTION trg_log_changes()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO "SEC.CHANGE_LOG" (TABLE_NAME, OPERATION_TYPE, ROW_ID, CHANGED_BY)
    VALUES (
        TG_TABLE_NAME,
        TG_OP,
        CASE WHEN TG_OP = 'DELETE' THEN OLD.ID ELSE NEW.ID END,
        SESSION_USER
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
--Reservation Table Trigger
DROP TRIGGER IF EXISTS trg_log_reservation_changes ON "reserves.reservation";
CREATE TRIGGER trg_log_reservation_changes
AFTER INSERT OR UPDATE OR DELETE ON "reserves.reservation"
FOR EACH ROW
EXECUTE FUNCTION trg_log_changes();
--Invoice Table Trigger
DROP TRIGGER IF EXISTS trg_log_invoice_changes ON "FINANCE.INVOICE";
CREATE TRIGGER trg_log_invoice_changes
AFTER INSERT OR UPDATE OR DELETE ON "FINANCE.INVOICE"
FOR EACH ROW
EXECUTE FUNCTION trg_log_changes();

/*
███████ ██████          ██       ██████   ██████           █████  ██    ██ ██████  ██ ████████ 
██      ██   ██         ██      ██    ██ ██               ██   ██ ██    ██ ██   ██ ██    ██    
███████ ██████          ██      ██    ██ ██   ███         ███████ ██    ██ ██   ██ ██    ██    
     ██ ██              ██      ██    ██ ██    ██         ██   ██ ██    ██ ██   ██ ██    ██    
███████ ██      ███████ ███████  ██████   ██████  ███████ ██   ██  ██████  ██████  ██    ██    
                                                                                               
*/
CREATE OR REPLACE PROCEDURE sp_log_audit(
    _username TEXT,
    _action_type TEXT,
    _table_name TEXT DEFAULT NULL,
    _row_id INT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO "SEC.AUDIT_LOG" (USERNAME, ACTION_TYPE, TABLE_NAME, ROW_ID)
    VALUES (_username, _action_type, _table_name, _row_id);

    RAISE NOTICE 'Action logged: User %, Action %', _username, _action_type;
END;
$$;




--IDFK WHETHER THIS WILL BE USED LIKE THIS OR NOT, TBD
CREATE OR REPLACE FUNCTION fn_user_login(
    _email VARCHAR(100),
    _hashed_password TEXT
) RETURNS TABLE (
    user_id INT,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(100),
    role_description VARCHAR(100),
    user_type CHAR(1) 
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        u.ID AS user_id,
        u.first_name,
        u.last_name,
        u.email,
        CASE
            WHEN u.utp = 'F' THEN (SELECT PERM_DESCRIPTION FROM "SEC.ACC_PERMISSIONS" ap WHERE ap.ID = e.role_id)
            ELSE 'Client'
        END AS role_description,
        u.utp AS user_type
    FROM "HR.USERS" u
    LEFT JOIN "HR.U_EMPLOYEE" e ON u.ID = e.ID
    WHERE u.email = _email
      AND u.hashed_password = _hashed_password
      AND u.inactive = FALSE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Invalid credentials or user is inactive.';
    END IF;

    -- Log the successful login in the audit log
    CALL sp_log_audit(
        _username := _email,
        _action_type := 'LOGIN',
        _table_name := 'HR.USERS',
        _row_id := (SELECT ID FROM HR.USERS WHERE email = _email)
    );
END;
$$ LANGUAGE plpgsql;

