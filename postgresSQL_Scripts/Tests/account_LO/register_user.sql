CREATE OR REPLACE FUNCTION TEST_register_user(
    _first_name VARCHAR(100),
    _last_name VARCHAR(100),
    _email VARCHAR(100),
    _hashed_password TEXT,
    _nif VARCHAR(20),
    _phone VARCHAR(20),
    _full_address VARCHAR(160),
    _postal_code VARCHAR(8),
    _city VARCHAR(100),
    _utp CHAR(1)
)
RETURNS TEXT AS $$
DECLARE
    record_count INTEGER;
    result TEXT;
BEGIN
    -- Call the sp_register_user procedure
    CALL sp_register_user(
        _first_name,
        _last_name,
        _email,
        _hashed_password,
        _nif,
        _phone,
        _full_address,
        _postal_code,
        _city,
        _utp
    );

    -- Check if the user has been successfully inserted
    SELECT COUNT(*)
    INTO record_count
    FROM "hr.users"
    WHERE first_name = _first_name
      AND last_name = _last_name
      AND email = _email;

    -- Determine test result
    IF record_count > 0 THEN
        result := 'OK';
    ELSE
        result := 'NOK';
    END IF;

    RETURN result;
END $$ LANGUAGE plpgsql;

-- Example test invocation
SELECT TEST_register_user(
    'John',
    'Doe',
    'john.doe@example.com',
    'hashed_password_example',
    '123456789',
    '987654321',
    '123 Example Street',
    '3500-678',
    'Example City',
    'C'
);
