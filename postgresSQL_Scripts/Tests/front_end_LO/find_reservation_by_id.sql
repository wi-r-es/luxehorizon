CREATE OR REPLACE FUNCTION test_fn_find_reservation_by_id()
RETURNS TEXT AS $$
DECLARE
    test_reservation_id BIGINT := 1; -- Replace with a valid reservation ID
    reservation_found BOOLEAN;
    reservation_record RECORD;
BEGIN
    -- Check if the reservation exists using the function
    SELECT EXISTS(
        SELECT 1
        FROM fn_find_reservation_by_id(test_reservation_id)
    ) INTO reservation_found;

    IF NOT reservation_found THEN
        RAISE EXCEPTION 'Test failed: Reservation ID % not found.', test_reservation_id;
    END IF;

    -- Fetch the reservation record to validate its details
    SELECT * INTO reservation_record
    FROM fn_find_reservation_by_id(test_reservation_id);

    -- Validate fields
    IF reservation_record.reservation_id IS NULL THEN
        RAISE EXCEPTION 'Test failed: Reservation ID is NULL.';
    END IF;

    IF reservation_record.client_id IS NULL THEN
        RAISE EXCEPTION 'Test failed: Client ID is NULL.';
    END IF;

    IF reservation_record.begin_date IS NULL OR reservation_record.end_date IS NULL THEN
        RAISE EXCEPTION 'Test failed: Begin or End Date is NULL.';
    END IF;

    IF reservation_record.total_value IS NULL OR reservation_record.total_value <= 0 THEN
        RAISE EXCEPTION 'Test failed: Total value is invalid (%).', reservation_record.total_value;
    END IF;

    IF reservation_record.status IS NULL OR LENGTH(TRIM(reservation_record.status)) != 2 THEN
        RAISE EXCEPTION 'Test failed: Status is invalid (%).', reservation_record.status;
    END IF;

    RAISE NOTICE 'Test passed: Reservation ID %, Client ID %, Total Value %, Status %.',
                 reservation_record.reservation_id,
                 reservation_record.client_id,
                 reservation_record.total_value,
                 reservation_record.status;

    RETURN 'Test passed for fn_find_reservation_by_id';
END;
$$ LANGUAGE plpgsql;

-- Run the test
SELECT test_fn_find_reservation_by_id();


-- to see outcome
select fn_find_reservation_by_id(1);
