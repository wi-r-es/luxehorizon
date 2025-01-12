CREATE OR REPLACE FUNCTION test_get_overview()
RETURNS TEXT AS $$
DECLARE
    total_revenue NUMERIC;
    expected_guests BIGINT;
BEGIN

    SELECT * INTO total_revenue, expected_guests FROM get_overview();

    IF total_revenue IS NULL THEN
        RAISE EXCEPTION 'Test failed: total_revenue is NULL.';
    END IF;

    IF expected_guests IS NULL THEN
        RAISE EXCEPTION 'Test failed: expected_guests is NULL.';
    END IF;

    RAISE NOTICE 'Test passed: total_revenue = %, expected_guests = %', total_revenue, expected_guests;
    RETURN 'Test passed for get_overview';
END;
$$ LANGUAGE plpgsql;

-- Run the test
SELECT test_get_overview();

-- to see outcome
SELECT * FROM get_overview();
