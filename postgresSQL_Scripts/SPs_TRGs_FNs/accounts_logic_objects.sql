/*
███████ ██████          ██████  ███████  ██████  ██ ███████ ████████ ███████ ██████          ██    ██ ███████ ███████ ██████  
██      ██   ██         ██   ██ ██      ██       ██ ██         ██    ██      ██   ██         ██    ██ ██      ██      ██   ██ 
███████ ██████          ██████  █████   ██   ███ ██ ███████    ██    █████   ██████          ██    ██ ███████ █████   ██████  
     ██ ██              ██   ██ ██      ██    ██ ██      ██    ██    ██      ██   ██         ██    ██      ██ ██      ██   ██ 
███████ ██      ███████ ██   ██ ███████  ██████  ██ ███████    ██    ███████ ██   ██ ███████  ██████  ███████ ███████ ██   ██ 
                                                                                                                              
*/
-- SP TO REGISTER A NEW USER (CLIENT OR EMPLOYEE)
CREATE OR REPLACE PROCEDURE MANAGEMENT.sp_register_user(
    _first_name VARCHAR(100),
    _last_name VARCHAR(100),
    _email VARCHAR(100),
    _hashed_password TEXT, -- Pre-hashed password in python /django
    _nif VARCHAR(20),
    _phone VARCHAR(20),
    _full_address VARCHAR(160),
    _postal_code VARCHAR(8),
    _city VARCHAR(100),
    _utp CHAR(1) DEFAULT 'C' 
)
LANGUAGE plpgsql
AS $$
DECLARE
    msg text;
    hint text;
    content text;
BEGIN
    -- Validate input for email uniqueness | can also be done via django instead 
    IF EXISTS (
        SELECT 1 
        FROM HR.USERS 
        WHERE EMAIL = _email
    ) THEN
        RAISE EXCEPTION 'Email % is already registered', _email;
    END IF;

    BEGIN -- PostgreSQL automatically wraps the BEGIN block in a transaction, so there’s no need for explicit BEGIN TRAN or COMMIT TRAN
        
        INSERT INTO HR.USERS (
            FIRST_NAME, LAST_NAME, EMAIL, HASHED_PASSWORD, NIF, PHONE, 
            FULL_ADDRESS, POSTAL_CODE, CITY, UTP
        ) VALUES (
            _first_name, _last_name, _email, _hashed_password, _nif, _phone, 
            _full_address, _postal_code, _city, _utp
        );
        RAISE NOTICE 'User % registered successfully', _email;
     EXCEPTION WHEN OTHERS THEN
        msg = MESSAGE_TEXT,
        content = PG_EXCEPTION_DETAIL,
        hint = PG_EXCEPTION_HINT;
            -- Log the error into the error table
            CALL SEC.LogError(msg, hint, content );

            RAISE;
    END;    
END;
$$;


/*
████████ ██████   ██████          ██████  ███████ ███████  █████  ██    ██ ██      ████████         
   ██    ██   ██ ██               ██   ██ ██      ██      ██   ██ ██    ██ ██         ██            
   ██    ██████  ██   ███         ██   ██ █████   █████   ███████ ██    ██ ██         ██            
   ██    ██   ██ ██    ██         ██   ██ ██      ██      ██   ██ ██    ██ ██         ██            
   ██    ██   ██  ██████  ███████ ██████  ███████ ██      ██   ██  ██████  ███████    ██    ███████ 
                                                                                                    
██████   ██████  ██      ███████         ███████  ██████  ██████          ███████ ███    ███ ██████  ██       ██████  ██    ██ ███████ ███████ 
██   ██ ██    ██ ██      ██              ██      ██    ██ ██   ██         ██      ████  ████ ██   ██ ██      ██    ██  ██  ██  ██      ██      
██████  ██    ██ ██      █████           █████   ██    ██ ██████          █████   ██ ████ ██ ██████  ██      ██    ██   ████   █████   █████   
██   ██ ██    ██ ██      ██              ██      ██    ██ ██   ██         ██      ██  ██  ██ ██      ██      ██    ██    ██    ██      ██      
██   ██  ██████  ███████ ███████ ███████ ██       ██████  ██   ██ ███████ ███████ ██      ██ ██      ███████  ██████     ██    ███████ ███████ 
                                                                                                                                                                                                                                                                                                                                                                                           
                                                                                                                                                                                                                                                   
*/
-- Assign default role for employee
CREATE OR REPLACE FUNCTION MANAGEMENT.trg_default_role_for_employee()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if the user type is 'F' (employee)
    IF NEW.UTP = 'F' THEN
        NEW.ROLE_ID := 3; -- Default to "Funcionario"
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER trg_default_role_for_employee
BEFORE INSERT ON HR.U_EMPLOYEE
FOR EACH ROW
EXECUTE FUNCTION MANAGEMENT.trg_default_role_for_employee();

/*
███████ ██████          ██    ██ ██████  ██████   █████  ████████ ███████         
██      ██   ██         ██    ██ ██   ██ ██   ██ ██   ██    ██    ██              
███████ ██████          ██    ██ ██████  ██   ██ ███████    ██    █████           
     ██ ██              ██    ██ ██      ██   ██ ██   ██    ██    ██              
███████ ██      ███████  ██████  ██      ██████  ██   ██    ██    ███████ ███████ 
                                                                                  
███████ ███    ███ ██████  ██       ██████  ██    ██ ███████ ███████         ██████   ██████  ██      ███████ 
██      ████  ████ ██   ██ ██      ██    ██  ██  ██  ██      ██              ██   ██ ██    ██ ██      ██      
█████   ██ ████ ██ ██████  ██      ██    ██   ████   █████   █████           ██████  ██    ██ ██      █████   
██      ██  ██  ██ ██      ██      ██    ██    ██    ██      ██              ██   ██ ██    ██ ██      ██      
███████ ██      ██ ██      ███████  ██████     ██    ███████ ███████ ███████ ██   ██  ██████  ███████ ███████ 
                                                                                                              
                                                                                                                                                                                                
*/
-- SP TO ASSING A new ROLE TO A EMPLOYEE, VIA ITS ID
CREATE OR REPLACE PROCEDURE MANAGEMENT.sp_update_employee_role(
    _user_id INT,
    _new_role_id INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    _is_employee BOOLEAN;
    msg TEXT;
    content TEXT;
    hint TEXT;
BEGIN
    -- Validate if the user is an employee
    SELECT EXISTS (
        SELECT 1
        FROM HR.U_EMPLOYEE
        WHERE ID = _user_id
    ) INTO _is_employee;

    IF NOT _is_employee THEN
        RAISE EXCEPTION 'User ID % is not an employee', _user_id;
    END IF;

    IF _new_role_id NOT IN (1, 2, 3) THEN
        RAISE EXCEPTION 'Invalid role ID %. Only 1 (Admin), 2 (Manager) or 3 (Employee) are allowed', _new_role_id;
    END IF;
    BEGIN
        UPDATE HR.U_EMPLOYEE
        SET ROLE_ID = _new_role_id
        WHERE ID = _user_id;

        RAISE NOTICE 'User ID % role updated to %', _user_id, _new_role_id;
    EXCEPTION WHEN OTHERS THEN
        msg = MESSAGE_TEXT,
        content = PG_EXCEPTION_DETAIL,
        hint = PG_EXCEPTION_HINT;
            CALL SEC.LogError(msg, hint, content );

            RAISE;
    END;    
END;
$$;



/*
███████ ██████          ██    ██ ██████  ██████   █████  ████████ ███████         
██      ██   ██         ██    ██ ██   ██ ██   ██ ██   ██    ██    ██              
███████ ██████          ██    ██ ██████  ██   ██ ███████    ██    █████           
     ██ ██              ██    ██ ██      ██   ██ ██   ██    ██    ██              
███████ ██      ███████  ██████  ██      ██████  ██   ██    ██    ███████ ███████ 


██    ██ ███████ ███████ ██████          ███████ ████████  █████  ████████ ██    ██ ███████ 
██    ██ ██      ██      ██   ██         ██         ██    ██   ██    ██    ██    ██ ██      
██    ██ ███████ █████   ██████          ███████    ██    ███████    ██    ██    ██ ███████ 
██    ██      ██ ██      ██   ██              ██    ██    ██   ██    ██    ██    ██      ██ 
 ██████  ███████ ███████ ██   ██ ███████ ███████    ██    ██   ██    ██     ██████  ███████ 
                                                                                            
                                                                                                                                                                                                                                                                                                                                                     
*/
CREATE OR REPLACE PROCEDURE MANAGEMENT.sp_update_user_status(
    _user_id INT,
    _inactive BOOLEAN
)
LANGUAGE plpgsql
AS $$
DECLARE
    _user_exists BOOLEAN;
    msg TEXT;
    content TEXT;
    hint TEXT;
BEGIN
    -- Check if the user exists
    SELECT EXISTS (
        SELECT 1 
        FROM HR.USERS
        WHERE ID = _user_id
    ) INTO _user_exists;

    IF NOT _user_exists THEN
        RAISE EXCEPTION 'User ID % does not exist', _user_id;
    END IF;

    BEGIN 
        UPDATE HR.SERS
        SET INACTIVE = _inactive
        WHERE ID = _user_id;

        RAISE NOTICE 'User ID % status updated to %', _user_id, _inactive;
    EXCEPTION WHEN OTHERS THEN
        msg = MESSAGE_TEXT,
        content = PG_EXCEPTION_DETAIL,
        hint = PG_EXCEPTION_HINT;
            CALL SEC.LogError(msg, hint, content );

            RAISE;
    END;    
END;
$$;



