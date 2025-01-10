CREATE OR REPLACE FUNCTION TEST_generate_invoice(
    _reservation_id INT,
    _payment_method_id INT
)
RETURNS TEXT AS $$
DECLARE
    _invoice_id INT;
    invoice_exists BOOLEAN;
    invoice_details_valid BOOLEAN;
    result TEXT;
BEGIN
    -- Call the procedure to generate the invoice
    BEGIN
        CALL sp_generate_invoice(_reservation_id, _payment_method_id, _invoice_id);

        -- Verify the invoice was created
        SELECT EXISTS (
            SELECT 1
            FROM "finance.invoice"
            WHERE id = _invoice_id
              AND reservation_id = _reservation_id
        ) INTO invoice_exists;

        IF NOT invoice_exists THEN
            RETURN 'NOK: Invoice not created';
        END IF;

        -- Verify the invoice details
        SELECT CASE
                   WHEN reservation_id = _reservation_id
                    AND payment_method_id = _payment_method_id
                    AND invoice_status = FALSE -- Unpaid by default
                   THEN TRUE
                   ELSE FALSE
               END
        INTO invoice_details_valid
        FROM "finance.invoice"
        WHERE id = _invoice_id;

        IF invoice_details_valid THEN
            result := 'OK';
        ELSE
            result := 'NOK: Invoice details are invalid';
        END IF;
    EXCEPTION WHEN OTHERS THEN
        result := 'NOK: Procedure failed - ' || SQLERRM;
    END;

    RETURN result;
END $$ LANGUAGE plpgsql;


--Test invocation
SELECT TEST_generate_invoice(1, 1); 
