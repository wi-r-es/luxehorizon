CREATE OR REPLACE FUNCTION TEST_add_hotel(
    _name VARCHAR(100),
    _address VARCHAR(160),
    _postal_code VARCHAR(8),
    _city VARCHAR(100),
    _email VARCHAR(100),
    _telephone VARCHAR(20),
    _details VARCHAR(200),
    _stars INT
)
RETURNS TEXT AS $$
DECLARE
    hotel_exists BOOLEAN;
    result TEXT;
BEGIN
    -- Check if the hotel already exists based on name and address
    SELECT EXISTS (
        SELECT 1
        FROM "management.hotel"
        WHERE h_name = _name AND full_address = _address
    ) INTO hotel_exists;

    IF hotel_exists THEN
        RETURN 'NOK: Hotel already exists';
    END IF;

    -- Call the procedure to add the hotel
    BEGIN
        CALL sp_add_hotel(
            _name, _address, _postal_code, _city, _email, _telephone, _details, _stars
        );

        -- Verify the insertion
        SELECT EXISTS (
            SELECT 1
            FROM "management.hotel"
            WHERE h_name = _name AND full_address = _address
        ) INTO hotel_exists;

        IF hotel_exists THEN
            result := 'OK';
        ELSE
            result := 'NOK: Hotel not added correctly';
        END IF;
    EXCEPTION WHEN OTHERS THEN
        result := 'NOK: Procedure failed - ' || SQLERRM;
    END;

    RETURN result;
END $$ LANGUAGE plpgsql;

--Test invocation
SELECT TEST_add_hotel(
    'Grand Luxe Hotel',
    '123 Elm Street',
    '1234-678',
    'Some City',
    'info@luxehorizon.com',
    '123456789',
    'A luxurious 5-star hotel in the city center.',
    5
);
