CREATE OR REPLACE FUNCTION test_get_sales_over_time()
RETURNS TEXT AS $$
DECLARE
    record_count INT;
    invalid_day_count INT;
BEGIN

    SELECT COUNT(*) INTO record_count FROM get_sales_over_time();

    SELECT COUNT(*) INTO invalid_day_count
    FROM get_sales_over_time()
    WHERE day < 1 OR day > 31;

    IF record_count = 0 THEN
        RAISE EXCEPTION 'Test failed: No records returned.';
    END IF;

    IF invalid_day_count > 0 THEN
        RAISE EXCEPTION 'Test failed: Found invalid day values.';
    END IF;

    RAISE NOTICE 'Test passed: % records returned, no invalid days.', record_count;
    RETURN 'Test passed for get_sales_over_time';
END;
$$ LANGUAGE plpgsql;

-- Run the test
SELECT test_get_sales_over_time();


--to see outcome
SELECT * FROM get_sales_over_time();

