
/*
 ██████  ███████ ████████          █████  ██    ██  █████  ██ ██       █████  ██████  ██      ███████         ██████   ██████   ██████  ███    ███ ███████ 
██       ██         ██            ██   ██ ██    ██ ██   ██ ██ ██      ██   ██ ██   ██ ██      ██              ██   ██ ██    ██ ██    ██ ████  ████ ██      
██   ███ █████      ██            ███████ ██    ██ ███████ ██ ██      ███████ ██████  ██      █████           ██████  ██    ██ ██    ██ ██ ████ ██ ███████ 
██    ██ ██         ██            ██   ██  ██  ██  ██   ██ ██ ██      ██   ██ ██   ██ ██      ██              ██   ██ ██    ██ ██    ██ ██  ██  ██      ██ 
 ██████  ███████    ██    ███████ ██   ██   ████   ██   ██ ██ ███████ ██   ██ ██████  ███████ ███████ ███████ ██   ██  ██████   ██████  ██      ██ ███████ 
                                                                                                                                                           
*/
CREATE OR REPLACE FUNCTION fn_get_available_rooms(
    _begin_date DATE,
    _end_date DATE
) RETURNS TABLE (
    room_id INT,
    room_number INT,
    hotel_id INT,
    base_price NUMERIC(10, 2),
    capacity "room_capacity_type"
) AS $$
BEGIN
    RETURN QUERY
    SELECT r.ID, r.room_number, r.hotel_id, r.base_price, r.capacity
    FROM "room_management.room" r
    WHERE r.condition = 0 
      AND NOT EXISTS (
          SELECT 1
          FROM "reserves.room_reservation" rr
          INNER JOIN "reserves.reservation" res ON rr.reservation_id = res.ID
          WHERE rr.room_id = r.ID
            AND res.begin_date < _end_date
            AND res.end_date > _begin_date
      );
END;
$$ LANGUAGE plpgsql;

/*
███████ ██ ███    ██ ██████          ██████  ███████ ███████ ███████ ██████  ██    ██  █████  ████████ ██  ██████  ███    ██         ██████  ██    ██         ██ ██████  
██      ██ ████   ██ ██   ██         ██   ██ ██      ██      ██      ██   ██ ██    ██ ██   ██    ██    ██ ██    ██ ████   ██         ██   ██  ██  ██          ██ ██   ██ 
█████   ██ ██ ██  ██ ██   ██         ██████  █████   ███████ █████   ██████  ██    ██ ███████    ██    ██ ██    ██ ██ ██  ██         ██████    ████           ██ ██   ██ 
██      ██ ██  ██ ██ ██   ██         ██   ██ ██           ██ ██      ██   ██  ██  ██  ██   ██    ██    ██ ██    ██ ██  ██ ██         ██   ██    ██            ██ ██   ██ 
██      ██ ██   ████ ██████  ███████ ██   ██ ███████ ███████ ███████ ██   ██   ████   ██   ██    ██    ██  ██████  ██   ████ ███████ ██████     ██    ███████ ██ ██████  
                                                                                                                                                                         
*/
CREATE OR REPLACE FUNCTION fn_find_reservation_by_id(
    _reservation_id INT
) RETURNS TABLE (
    reservation_id INT,
    client_id INT,
    begin_date DATE,
    end_date DATE,
    total_value NUMERIC(10, 2),
    STATUS CHAR(2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT r.ID, r.client_id, r.begin_date, r.end_date, r.total_value, r.status
    FROM "reserves.reservation" r
    WHERE r.ID = _reservation_id;
END;
$$ LANGUAGE plpgsql;



/*
 ██████  █████  ██       ██████ ██    ██ ██       █████  ████████ ███████         ██████  ██████  ██  ██████ ███████ 
██      ██   ██ ██      ██      ██    ██ ██      ██   ██    ██    ██              ██   ██ ██   ██ ██ ██      ██      
██      ███████ ██      ██      ██    ██ ██      ███████    ██    █████           ██████  ██████  ██ ██      █████   
██      ██   ██ ██      ██      ██    ██ ██      ██   ██    ██    ██              ██      ██   ██ ██ ██      ██      
 ██████ ██   ██ ███████  ██████  ██████  ███████ ██   ██    ██    ███████ ███████ ██      ██   ██ ██  ██████ ███████                                                                                                                                                                                                                                                                                        
*/

/*
 * Returns the price of a given room to a given season, TO BE USED WITH THE FRONTEND MAINLY
 */
CREATE OR REPLACE FUNCTION fn_calculate_price(
    _room_id INT,
    _season_id INT
) RETURNS NUMERIC(10, 2) AS $$
DECLARE
    _base_price NUMERIC(10, 2);
    _tax_rate FLOAT;
    _total_price NUMERIC(10, 2);
BEGIN
    SELECT base_price INTO _base_price FROM "ROOM_MANAGEMENT.ROOM" WHERE ID = _room_id;

    SELECT TAX INTO _tax_rate FROM "FINANCE.PRICE_PER_SEASON" WHERE season_id = _season_id;

    _total_price := _base_price + (_base_price * _tax_rate );

    RETURN _total_price;
END;
$$ LANGUAGE plpgsql;
/*
 ██████  █████  ██       ██████ ██    ██ ██       █████  ████████ ███████         ████████  ██████  ████████  █████  ██              ██████  ██████  ██  ██████ ███████ 
██      ██   ██ ██      ██      ██    ██ ██      ██   ██    ██    ██                 ██    ██    ██    ██    ██   ██ ██              ██   ██ ██   ██ ██ ██      ██      
██      ███████ ██      ██      ██    ██ ██      ███████    ██    █████              ██    ██    ██    ██    ███████ ██              ██████  ██████  ██ ██      █████   
██      ██   ██ ██      ██      ██    ██ ██      ██   ██    ██    ██                 ██    ██    ██    ██    ██   ██ ██              ██      ██   ██ ██ ██      ██      
 ██████ ██   ██ ███████  ██████  ██████  ███████ ██   ██    ██    ███████ ███████    ██     ██████     ██    ██   ██ ███████ ███████ ██      ██   ██ ██  ██████ ███████ 
                                                                                                                                                                        
*/
CREATE OR REPLACE FUNCTION fn_calculate_total_price(
    _room_ids INT[],
    _tax_rate FLOAT
) RETURNS NUMERIC(10, 2) AS $$
DECLARE
    _total_price NUMERIC(10, 2) := 0;
    _room_price NUMERIC(10, 2);
BEGIN
    FOR _room_price IN
        SELECT base_price
        FROM "ROOM_MANAGEMENT.ROOM"
        WHERE ID = ANY(_room_ids)
    LOOP
        _total_price := _total_price + (_room_price + (_room_price * _tax_rate));
    END LOOP;

    RETURN _total_price;
END;
$$ LANGUAGE plpgsql;
