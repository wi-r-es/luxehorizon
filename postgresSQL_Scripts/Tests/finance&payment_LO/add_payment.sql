CREATE OR REPLACE FUNCTION TEST_add_payment(
    _invoice_id INT,
    _payment_amount NUMERIC(10, 2),
    _payment_method_id INT
)
RETURNS TEXT AS $$
DECLARE
    payment_exists BOOLEAN;
    invoice_status BOOLEAN;
    total_paid NUMERIC(10,2);
    final_value NUMERIC(10,2);
    remaining_balance NUMERIC(10,2);
    result TEXT;
BEGIN
    -- Call the procedure to add payment
    BEGIN
        CALL sp_add_payment(_invoice_id, _payment_amount, _payment_method_id);

        -- Verify that the payment was recorded
        SELECT EXISTS (
            SELECT 1 FROM "finance.payments"
            WHERE invoice_id = _invoice_id
              AND payment_amount = _payment_amount
              AND payment_method_id = _payment_method_id
        ) INTO payment_exists;

        IF NOT payment_exists THEN
            RETURN 'NOK: Payment not recorded';
        END IF;

        -- Retrieve invoice details
        SELECT invoice_status, final_value
        INTO invoice_status, final_value
        FROM "finance.invoice"
        WHERE id = _invoice_id;

        -- Calculate total paid amount
        SELECT COALESCE(SUM(payment_amount), 0)
        INTO total_paid
        FROM "finance.payments"
        WHERE invoice_id = _invoice_id;

        -- Calculate remaining balance
        remaining_balance := final_value - total_paid;

        -- Verify if the invoice is fully paid
        IF invoice_status AND remaining_balance <= 0 THEN
            result := 'OK: Invoice fully paid';
        ELSE
            result := 'OK: Partial payment recorded, remaining balance: ' || remaining_balance;
        END IF;
    EXCEPTION WHEN OTHERS THEN
        result := 'NOK: Procedure failed - ' || SQLERRM;
    END;

    RETURN result;
END $$ LANGUAGE plpgsql;

--Test invocation
SELECT TEST_add_payment(1, 4200.00, 1); -- Full payment
