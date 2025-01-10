CREATE OR REPLACE FUNCTION TEST_cancel_reservation(
    _reservation_id INT
)
RETURNS TEXT AS $$
DECLARE
    reservation_exists BOOLEAN;
    room_reservations_exist BOOLEAN;
    reservation_status TEXT;
    result TEXT;
BEGIN
    -- Call the procedure to cancel the reservation
    BEGIN
        CALL sp_cancel_reservation(_reservation_id);

        -- Verify the reservation status is updated
        SELECT status
        INTO reservation_status
        FROM "reserves.reservation"
        WHERE id = _reservation_id;

        IF reservation_status = 'CC' THEN
            result := 'OK';
        ELSE
            RETURN 'NOK: Reservation status not updated to Cancelled';
        END IF;

        -- Verify associated room reservations are deleted
        SELECT EXISTS (
            SELECT 1 
            FROM "reserves.room_reservation"
            WHERE reservation_id = _reservation_id
        ) INTO room_reservations_exist;

        IF room_reservations_exist THEN
            RETURN 'NOK: Associated room reservations not deleted';
        END IF;

    EXCEPTION WHEN OTHERS THEN
        result := 'NOK: Procedure failed - ' || SQLERRM;
    END;

    RETURN result;
END $$ LANGUAGE plpgsql;

--Test invocation
SELECT TEST_cancel_reservation(1); 
