/*
███████ ██████          ██████  ███████  ██████  ██ ███████ ████████ ███████ ██████          ██    ██ ███████ ███████ ██████  
██      ██   ██         ██   ██ ██      ██       ██ ██         ██    ██      ██   ██         ██    ██ ██      ██      ██   ██ 
███████ ██████          ██████  █████   ██   ███ ██ ███████    ██    █████   ██████          ██    ██ ███████ █████   ██████  
     ██ ██              ██   ██ ██      ██    ██ ██      ██    ██    ██      ██   ██         ██    ██      ██ ██      ██   ██ 
███████ ██      ███████ ██   ██ ███████  ██████  ██ ███████    ██    ███████ ██   ██ ███████  ██████  ███████ ███████ ██   ██ 
                                                                                                                              
*/
-- SP TO REGISTER A NEW USER (CLIENT OR EMPLOYEE)
CREATE OR REPLACE PROCEDURE sp_register_user( --tested
    _first_name VARCHAR(100),
    _last_name VARCHAR(100),
    _email VARCHAR(100),
    _hashed_password TEXT, -- Pre-hashed password in python /django
    _nif VARCHAR(20),
    _phone VARCHAR(20),
    _full_address VARCHAR(160),
    _postal_code VARCHAR(8),
    _city VARCHAR(100),
    _utp CHAR(1) DEFAULT 'C' ,
    _social_sec INT DEFAULT NULL,
    _is_active BOOLEAN DEFAULT True ,
    _is_staff BOOLEAN DEFAULT False,
    _is_superuser BOOLEAN DEFAULT False
)
LANGUAGE plpgsql
AS $$
DECLARE
    msg text;
    hint text;
    content text;
    _role_id  INT;
BEGIN
    -- Validate input for email uniqueness | can also be done via django instead 
    IF EXISTS (
        SELECT 1 
        FROM "hr.users" 
        WHERE email = _email
    ) THEN
        RAISE EXCEPTION 'Email % is already registered', _email;
    END IF;

    -- Check the value of _utp and assign an integer to _result
    _role_id := CASE
        WHEN _utp = 'C' THEN 4
        ELSE 3
    END;

    BEGIN -- PostgreSQL automatically wraps the BEGIN block in a transaction, so there’s no need for explicit BEGIN TRAN or COMMIT TRAN

        INSERT INTO "hr.users" ( password, role_id, social_security,
            first_name, last_name, email, hashed_password, nif, phone, 
            full_address, postal_code, city, utp, is_active, is_staff, is_superuser
        ) VALUES (_hashed_password, _role_id, _social_sec,
            _first_name, _last_name, _email, _hashed_password, _nif, _phone, 
            _full_address, _postal_code, _city, _utp, _is_active, _is_staff, _is_superuser
        );
        RAISE NOTICE 'User % registered successfully', _email;
    
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
CREATE OR REPLACE FUNCTION trg_default_role_for_employee() --TESTED
RETURNS TRIGGER AS $$
BEGIN
    -- Check if the user type is 'F' (employee)
    IF NEW.utp = 'F' THEN
        NEW.role_id := 3; -- Default to "Funcionario"
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_default_role_for_employee ON "hr.users";
CREATE TRIGGER trg_default_role_for_employee
BEFORE INSERT ON "hr.users"
FOR EACH ROW
EXECUTE FUNCTION trg_default_role_for_employee();

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
-- SP TO ASSING A new ROLE TO A EMPLOYEE, VIA ITS id
CREATE OR REPLACE PROCEDURE sp_update_employee_role( --TESTED
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
        FROM "hr.users"
        WHERE id = _user_id AND utp = 'F'
    ) INTO _is_employee;

    IF NOT _is_employee THEN
        RAISE EXCEPTION 'User id % is not an employee', _user_id;
    END IF;

    IF _new_role_id NOT IN (1, 2, 3) THEN
        RAISE EXCEPTION 'Invalid role id %. Only 1 (Admin), 2 (Manager) or 3 (Employee) are allowed', _new_role_id;
    END IF;
    BEGIN
        UPDATE "hr.users"
        SET role_id = _new_role_id
        WHERE id = _user_id;

        RAISE NOTICE 'User id % role updated to %', _user_id, _new_role_id;
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
CREATE OR REPLACE PROCEDURE sp_update_user_status( --TESTESD
    _user_id INT,
    _is_active BOOLEAN
)
LANGUAGE plpgsql
AS $$
DECLARE
    _user_exists BOOLEAN;
    msg TEXT;
    content TEXT;
    hint TEXT;
BEGIN
    SELECT EXISTS (
        SELECT 1 
        FROM "hr.users"
        WHERE id = _user_id
    ) INTO _user_exists;

    IF NOT _user_exists THEN
        RAISE EXCEPTION 'User id % does not exist', _user_id;
    END IF;

    BEGIN 
        UPDATE "hr.users"
        SET is_active = _is_active
        WHERE id = _user_id;

        RAISE NOTICE 'User id % status updated to %', _user_id, _is_active;
    EXCEPTION WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS msg = MESSAGE_TEXT,
                                content = PG_EXCEPTION_DETAIL,
                                hint = PG_EXCEPTION_HINT;
        CALL sp_secLogError(msg, hint, content );

        RAISE NOTICE E'--- Call content ---\n%', content;
    END;    
END;
$$;



