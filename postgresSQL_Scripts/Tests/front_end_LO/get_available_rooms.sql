CREATE OR REPLACE FUNCTION test_fn_get_available_rooms()
RETURNS TEXT AS $$
DECLARE
    room_count INT;
BEGIN

    SELECT COUNT(*) INTO room_count
    FROM fn_get_available_rooms('2025-01-01', '2025-01-10');

    IF room_count = 0 THEN
        RAISE EXCEPTION 'Test failed: No available rooms found.';
    END IF;

    RAISE NOTICE 'Test passed: % available rooms found.', room_count;
    RETURN 'Test passed for fn_get_available_rooms';
END;
$$ LANGUAGE plpgsql;

-- Run the test
SELECT test_fn_get_available_rooms();

--TO SEE OUTCOME
SELECT * FROM fn_get_available_rooms('2025-01-01', '2025-01-10');


