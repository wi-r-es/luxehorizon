CREATE OR REPLACE FUNCTION TEST_update_tax(
    _season_id INT,
    _new_tax FLOAT
)
RETURNS TEXT AS $$
DECLARE
    updated_tax FLOAT;
    result TEXT;
BEGIN
    -- Call the procedure to update the tax
    BEGIN
        CALL sp_update_tax(_season_id, _new_tax);

        -- Verify the tax value is updated
        SELECT rate
        INTO updated_tax
        FROM "finance.season"
        WHERE id = _season_id;

        IF updated_tax = _new_tax THEN
            result := 'OK';
        ELSE
            result := 'NOK: Tax not updated correctly';
        END IF;
    EXCEPTION WHEN OTHERS THEN
        result := 'NOK: Procedure failed - ' || SQLERRM;
    END;

    RETURN result;
END $$ LANGUAGE plpgsql;

--Test invocation
SELECT TEST_update_tax(1, 100); 




