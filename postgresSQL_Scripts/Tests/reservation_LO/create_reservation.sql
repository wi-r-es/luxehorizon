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
    result TEXT;
BEGIN
    -- Call the procedure to create a reservation
    BEGIN
        CALL sp_create_reservation(user_id, room_id, checkin, checkout, guests);

        -- Verify the reservation exists
        SELECT EXISTS (
            SELECT 1
            FROM "reserves.reservation" r
            JOIN "reserves.room_reservation" rr ON r.id = rr.reservation_id
            WHERE r.client_id = user_id 
              AND rr.room_id = room_id
              AND r.begin_date = checkin 
              AND r.end_date = checkout
        ) INTO reservation_exists;

        IF reservation_exists THEN
            result := 'OK';
        ELSE
            result := 'NOK: Reservation not created correctly';
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
    '2025-05-01', 
    '2025-05-05', 
    2             
);
