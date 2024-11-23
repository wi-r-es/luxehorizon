CREATE OR REPLACE FUNCTION RESERVES.fn_get_available_rooms(
    _begin_date DATE,
    _end_date DATE
) RETURNS TABLE (
    ROOM_ID INT,
    ROOM_NUMBER INT,
    HOTEL_ID INT,
    BASE_PRICE NUMERIC(10, 2),
    CAPACITY ROOM_MANAGEMENT.capacity_type
) AS $$
BEGIN
    RETURN QUERY
    SELECT r.ID, r.ROOM_NUMBER, r.HOTEL_ID, r.BASE_PRICE, r.CAPACITY
    FROM ROOM_MANAGEMENT.ROOM r
    WHERE r.CONDITION = 0 
      AND NOT EXISTS (
          SELECT 1
          FROM RESERVES.ROOM_RESERVATION rr
          INNER JOIN RESERVES.RESERVATION res ON rr.RESERVATION_ID = res.ID
          WHERE rr.ROOM_ID = r.ID
            AND res.BEGIN_DATE < _end_date
            AND res.END_DATE > _begin_date
      );
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION RESERVES.fn_find_reservation_by_id(
    _reservation_id INT
) RETURNS TABLE (
    RESERVATION_ID INT,
    CLIENT_ID INT,
    BEGIN_DATE DATE,
    END_DATE DATE,
    TOTAL_VALUE NUMERIC(10, 2),
    STATUS CHAR(2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT r.ID, r.CLIENT_ID, r.BEGIN_DATE, r.END_DATE, r.TOTAL_VALUE, r.R_DETAIL
    FROM RESERVES.RESERVATION r
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
CREATE OR REPLACE FUNCTION RESERVES.fn_calculate_price(
    _room_id INT,
    _season_id INT
) RETURNS NUMERIC(10, 2) AS $$
DECLARE
    _base_price NUMERIC(10, 2);
    _tax_rate FLOAT;
    _total_price NUMERIC(10, 2);
BEGIN
    SELECT BASE_PRICE INTO _base_price FROM ROOM_MANAGEMENT.ROOM WHERE ID = _room_id;

    SELECT TAX INTO _tax_rate FROM FINANCE.PRICE_PER_SEASON WHERE SEASON_ID = _season_id;

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
CREATE OR REPLACE FUNCTION FINANCE.fn_calculate_total_price(
    _room_ids INT[],
    _tax_rate FLOAT
) RETURNS NUMERIC(10, 2) AS $$
DECLARE
    _total_price NUMERIC(10, 2) := 0;
    _room_price NUMERIC(10, 2);
BEGIN
    FOR _room_price IN
        SELECT BASE_PRICE
        FROM ROOM_MANAGEMENT.ROOM
        WHERE ID = ANY(_room_ids)
    LOOP
        _total_price := _total_price + (_room_price + (_room_price * _tax_rate));
    END LOOP;

    RETURN _total_price;
END;
$$ LANGUAGE plpgsql;
