CREATE OR REPLACE FUNCTION TEST_create_reservation(
    user_id INTEGER,
    room_id INTEGER,
    checkin DATE,
    checkout DATE,
    guests INTEGER
)
RETURNS TEXT AS $$
DECLARE
    reservation_exists BOOLEAN;
    total_value NUMERIC;
    result TEXT;
BEGIN
    -- Call the procedure to create the reservation
    BEGIN
        CALL create_reservation(user_id, room_id, checkin, checkout, guests);

        -- Verify the reservation exists
        SELECT EXISTS (
            SELECT 1
            FROM "reserves.reservation"
            WHERE client_id = user_id AND begin_date = checkin AND end_date = checkout
        ) INTO reservation_exists;

        IF reservation_exists THEN
            -- Fetch the total value of the reservation for validation
            SELECT total_value INTO total_value
            FROM "reserves.reservation"
            WHERE client_id = user_id AND begin_date = checkin AND end_date = checkout;

            IF total_value > 0 THEN
                result := 'OK: Reservation created successfully.';
            ELSE
                result := 'NOK: Reservation created but total price is invalid.';
            END IF;
        ELSE
            result := 'NOK: Reservation not created.';
        END IF;
    EXCEPTION WHEN OTHERS THEN
        result := 'NOK: Procedure failed - ' || SQLERRM;
    END;

    RETURN result;
END $$ LANGUAGE plpgsql;

--Test invocation
SELECT TEST_create_reservation(
    1, 
    1, 
    '2025-01-10', 
    '2025-01-15', 
    2 
);