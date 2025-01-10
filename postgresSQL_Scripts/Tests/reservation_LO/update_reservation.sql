CREATE OR REPLACE FUNCTION TEST_update_reservation(
    _reservation_id INT,
    _new_begin_date DATE,
    _new_end_date DATE,
    _new_room_ids INT[]
)
RETURNS TEXT AS $$
DECLARE
    updated_reservation_exists BOOLEAN;
    result TEXT;
    calculated_total_price NUMERIC;
BEGIN
    -- Call the procedure to update the reservation
    BEGIN
        CALL sp_update_reservation(_reservation_id, _new_begin_date, _new_end_date, _new_room_ids);

        -- Verify the updated reservation exists
        SELECT EXISTS (
            SELECT 1
            FROM "reserves.reservation" r
            JOIN "reserves.room_reservation" rr ON r.id = rr.reservation_id
            WHERE r.id = _reservation_id
              AND r.begin_date = _new_begin_date
              AND r.end_date = _new_end_date
        ) INTO updated_reservation_exists;

        IF NOT updated_reservation_exists THEN
            RETURN 'NOK: Reservation update failed';
        END IF;

        -- Optionally, validate the total price
        SELECT SUM(rr.price_reservation)
        INTO calculated_total_price
        FROM "reserves.room_reservation" rr
        WHERE rr.reservation_id = _reservation_id;

        IF calculated_total_price IS NULL OR calculated_total_price <= 0 THEN
            RETURN 'NOK: Total price calculation failed';
        END IF;

        result := 'OK';
    EXCEPTION WHEN OTHERS THEN
        result := 'NOK: Procedure failed - ' || SQLERRM;
    END;

    RETURN result;
END $$ LANGUAGE plpgsql;


--Test invocation
SELECT TEST_update_reservation(
    1,                -- Reservation ID
    '2025-05-02',     -- New begin date
    '2025-05-06',     -- New end date
    ARRAY[1, 2]       -- New room IDs
);