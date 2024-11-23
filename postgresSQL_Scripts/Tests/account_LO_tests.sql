CREATE OR REPLACE FUNCTION TEST_sp_register_user(
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
    inserted_count INT;
    result TEXT;
BEGIN

    BEGIN
        CALL MANAGEMENT.sp_register_user(
            _first_name, _last_name, _email, _hashed_password,
            _nif, _phone, _full_address, _postal_code, _city, _utp
        );
    EXCEPTION WHEN OTHERS THEN
        RETURN 'Error: ' || SQLERRM;
    END;

    SELECT COUNT(*) INTO inserted_count
    FROM HR.USERS
    WHERE FIRST_NAME = _first_name
      AND LAST_NAME = _last_name
      AND EMAIL = _email
      AND NIF = _nif
      AND PHONE = _phone
      AND FULL_ADDRESS = _full_address
      AND POSTAL_CODE = _postal_code
      AND CITY = _city
      AND UTP = _utp;

    IF inserted_count > 0 THEN
        result := 'OK';
    ELSE
        result := 'NOK';
    END IF;

    RETURN result;
END;
$$ LANGUAGE plpgsql;
