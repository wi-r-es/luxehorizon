/*
███████ ██████           ██████  ███████ ███    ██ ███████ ██████   █████  ████████ ███████         ██ ███    ██ ██    ██  ██████  ██  ██████ ███████ 
██      ██   ██         ██       ██      ████   ██ ██      ██   ██ ██   ██    ██    ██              ██ ████   ██ ██    ██ ██    ██ ██ ██      ██      
███████ ██████          ██   ███ █████   ██ ██  ██ █████   ██████  ███████    ██    █████           ██ ██ ██  ██ ██    ██ ██    ██ ██ ██      █████   
     ██ ██              ██    ██ ██      ██  ██ ██ ██      ██   ██ ██   ██    ██    ██              ██ ██  ██ ██  ██  ██  ██    ██ ██ ██      ██      
███████ ██      ███████  ██████  ███████ ██   ████ ███████ ██   ██ ██   ██    ██    ███████ ███████ ██ ██   ████   ████    ██████  ██  ██████ ███████                                                                                                                                      
 */


CREATE OR REPLACE PROCEDURE sp_generate_invoice(
    _reservation_id INT,
    _payment_method_id INT,
    OUT _invoice_id INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    _client_id INT;
    _total_value NUMERIC(10, 2);
    _emission_date DATE := CURRENT_DATE;
    msg TEXT;
    content TEXT;
    hint TEXT;
BEGIN
    SELECT client_id, total_value
    INTO _client_id, _total_value
    FROM "reserves.reservation"
    WHERE id = _reservation_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Reservation id % does not exist.', _reservation_id;
    END IF;

    BEGIN
        INSERT INTO "finance.invoice" (
            reservation_id, client_id, final_value, emission_date, billing_date,
            invoice_status, payment_method_id
        ) VALUES (
            _reservation_id, _client_id, _total_value, _emission_date, NULL,
            FALSE, _payment_method_id -- Unpaid by default
        )
        RETURNING id INTO _invoice_id;

        RAISE NOTICE 'Invoice id % generated successfully for Reservation id %', _invoice_id, _reservation_id;
    EXCEPTION WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS msg = MESSAGE_TEXT,
                                content = PG_EXCEPTION_DETAIL,
                                hint = PG_EXCEPTION_HINT;
        CALL sp_secLogError(msg, hint, content );

        RAISE NOTICE E'--- Call content ---\n%', content;
    END;    
END;
$$;


/*
███████ ██████           █████  ██████  ██████          ██████   █████  ██    ██ ███    ███ ███████ ███    ██ ████████ 
██      ██   ██         ██   ██ ██   ██ ██   ██         ██   ██ ██   ██  ██  ██  ████  ████ ██      ████   ██    ██    
███████ ██████          ███████ ██   ██ ██   ██         ██████  ███████   ████   ██ ████ ██ █████   ██ ██  ██    ██    
     ██ ██              ██   ██ ██   ██ ██   ██         ██      ██   ██    ██    ██  ██  ██ ██      ██  ██ ██    ██    
███████ ██      ███████ ██   ██ ██████  ██████  ███████ ██      ██   ██    ██    ██      ██ ███████ ██   ████    ██    
                                                                                                                                                                                                                                                                        
*/
CREATE OR REPLACE PROCEDURE sp_add_payment(
    _invoice_id INT,
    _payment_amount NUMERIC(10, 2),
    _payment_method_id INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    _final_value NUMERIC(10, 2);
    _current_paid NUMERIC(10, 2);
    _payment_id INT;
    msg TEXT;
    content TEXT;
    hint TEXT;
BEGIN
    SELECT final_value, COALESCE(SUM(p.payment_amount), 0)
    INTO _final_value, _current_paid
    FROM "finance.invoice" i
    LEFT JOIN finance.payments p ON i.id = p.invoice_id
    WHERE i.id = _invoice_id
    GROUP BY i.final_value;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Invoice id % does not exist.', _invoice_id;
    END IF;
    BEGIN
        INSERT INTO finance.payments (
            invoice_id, payment_amount, payment_date, payment_method_id
        ) VALUES (
            _invoice_id, _payment_amount, CURRENT_DATE, _payment_method_id
        )
        RETURNING id INTO _payment_id;

        -- Update the INVOICE table if fully paid. 
        IF _current_paid + _payment_amount >= _final_value THEN
            UPDATE "finance.invoice"
            SET payment_id = _payment_id,
                billing_date = CURRENT_TIMESTAMP,
                invoice_status = TRUE
            WHERE id = _invoice_id;

            RAISE NOTICE 'Invoice id % is now fully paid.', _invoice_id;
        ELSE
            RAISE NOTICE 'Partial payment recorded for Invoice id %. Remaining balance: %.',
                _invoice_id, _final_value - (_current_paid + _payment_amount);
        END IF;
    EXCEPTION WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS msg = MESSAGE_TEXT,
                                content = PG_EXCEPTION_DETAIL,
                                hint = PG_EXCEPTION_HINT;
        CALL sp_secLogError(msg, hint, content );

        RAISE NOTICE E'--- Call content ---\n%', content;
    END;    
END;
$$;


/*
████████ ██████   ██████          ██    ██ ██████  ██████   █████  ████████ ███████ 
   ██    ██   ██ ██               ██    ██ ██   ██ ██   ██ ██   ██    ██    ██      
   ██    ██████  ██   ███         ██    ██ ██████  ██   ██ ███████    ██    █████   
   ██    ██   ██ ██    ██         ██    ██ ██      ██   ██ ██   ██    ██    ██      
   ██    ██   ██  ██████  ███████  ██████  ██      ██████  ██   ██    ██    ███████ 
                                                                                    
██████  ███████ ███████ ███████ ██████  ██    ██  █████  ████████ ██  ██████  ███    ██         
██   ██ ██      ██      ██      ██   ██ ██    ██ ██   ██    ██    ██ ██    ██ ████   ██         
██████  █████   ███████ █████   ██████  ██    ██ ███████    ██    ██ ██    ██ ██ ██  ██         
██   ██ ██           ██ ██      ██   ██  ██  ██  ██   ██    ██    ██ ██    ██ ██  ██ ██         
██   ██ ███████ ███████ ███████ ██   ██   ████   ██   ██    ██    ██  ██████  ██   ████ ███████ 

███████ ████████  █████  ████████ ██    ██ ███████          ██████  ███    ██         ██████   █████  ██    ██ ███    ███ ███████ ███    ██ ████████ 
██         ██    ██   ██    ██    ██    ██ ██              ██    ██ ████   ██         ██   ██ ██   ██  ██  ██  ████  ████ ██      ████   ██    ██    
███████    ██    ███████    ██    ██    ██ ███████         ██    ██ ██ ██  ██         ██████  ███████   ████   ██ ████ ██ █████   ██ ██  ██    ██    
     ██    ██    ██   ██    ██    ██    ██      ██         ██    ██ ██  ██ ██         ██      ██   ██    ██    ██  ██  ██ ██      ██  ██ ██    ██    
███████    ██    ██   ██    ██     ██████  ███████ ███████  ██████  ██   ████ ███████ ██      ██   ██    ██    ██      ██ ███████ ██   ████    ██    
                                                                                                                                                     
*/
CREATE OR REPLACE FUNCTION trg_update_reservation_status_on_payment()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.invoice_status = TRUE THEN
        UPDATE "reserves.reservation"
        SET status = 'C' -- confirmada
        WHERE id = NEW.reservation_id;

        RAISE NOTICE 'Reservation id % is now marked as Paid.', NEW.reservation_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_update_reservation_status_on_payment ON "finance.invoice";
CREATE TRIGGER trg_update_reservation_status_on_payment
AFTER UPDATE OF invoice_status ON "finance.invoice"
FOR EACH ROW
EXECUTE FUNCTION trg_update_reservation_status_on_payment();




/*
███████ ██████          ██    ██ ██████  ██████   █████  ████████ ███████         ████████  █████  ██   ██ 
██      ██   ██         ██    ██ ██   ██ ██   ██ ██   ██    ██    ██                 ██    ██   ██  ██ ██  
███████ ██████          ██    ██ ██████  ██   ██ ███████    ██    █████              ██    ███████   ███   
     ██ ██              ██    ██ ██      ██   ██ ██   ██    ██    ██                 ██    ██   ██  ██ ██  
███████ ██      ███████  ██████  ██      ██████  ██   ██    ██    ███████ ███████    ██    ██   ██ ██   ██ 
                                                                                                           
*/
CREATE OR REPLACE PROCEDURE sp_update_tax(
    _season_id INT,
    _new_tax FLOAT
)
LANGUAGE plpgsql
AS $$
DECLARE
    _existing_tax FLOAT;
    msg TEXT;
    content TEXT;
    hint TEXT;
BEGIN
    SELECT TAX
    INTO _existing_tax
    FROM "finance.price_per_season"
    WHERE season_id = _season_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Season id % does not exist in PRICE_PER_SEASON.', _season_id;
    END IF;

    IF _new_tax < 0 OR _new_tax > 1.0 THEN
        RAISE EXCEPTION 'The new tax value % is invalid. It must be between 0 and 100.', _new_tax;
    END IF;

    BEGIN
        UPDATE "finance.price_per_season"
        SET TAX = _new_tax
        WHERE season_id = _season_id;

        RAISE NOTICE 'Tax for Season id % updated successfully to %.', _season_id, _new_tax;
    EXCEPTION WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS msg = MESSAGE_TEXT,
                                content = PG_EXCEPTION_DETAIL,
                                hint = PG_EXCEPTION_HINT;
        CALL sp_secLogError(msg, hint, content );

        RAISE NOTICE E'--- Call content ---\n%', content;
    END;    
END;
$$;

