CREATE OR REPLACE FUNCTION TEST_update_employee_role(
    _user_id INT,
    _new_role_id INT
)
RETURNS TEXT AS $$
DECLARE
    updated_role_id INT;
    is_employee BOOLEAN;
    result TEXT;
BEGIN
    -- Call the procedure to update the employee's role
    BEGIN
        CALL sp_update_employee_role(_user_id, _new_role_id);

        -- Verify that the role was updated
        SELECT role_id
        INTO updated_role_id
        FROM "hr.users"
        WHERE id = _user_id;

        IF updated_role_id = _new_role_id THEN
            result := 'OK';
        ELSE
            result := 'NOK: Role ID not updated correctly';
        END IF;
    EXCEPTION WHEN OTHERS THEN
        result := 'NOK: Procedure failed - ' || SQLERRM;
    END;

    RETURN result;
END $$ LANGUAGE plpgsql;

--Test invocation
SELECT TEST_update_employee_role(2, 2);