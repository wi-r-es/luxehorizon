CREATE OR REPLACE FUNCTION test_get_top_placements()
RETURNS TEXT AS $$
DECLARE
    record_count INT;
BEGIN
    SELECT COUNT(*) INTO record_count FROM get_top_placements();

    IF record_count > 5 THEN
        RAISE EXCEPTION 'Test failed: Returned more than 5 rows.';
    END IF;

    IF record_count = 0 THEN
        RAISE EXCEPTION 'Test failed: No records returned.';
    END IF;

    RAISE NOTICE 'Test passed: % records returned.', record_count;
    RETURN 'Test passed for get_top_placements';
END;
$$ LANGUAGE plpgsql;

-- Run the test
SELECT test_get_top_placements();

--To see the actual content
SELECT * FROM get_top_placements();