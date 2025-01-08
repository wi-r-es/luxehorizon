-- FUNCTION TO GET OVERVIEW SECTION IN DASHBOARD
CREATE OR REPLACE FUNCTION get_overview()
RETURNS TABLE(total_revenue NUMERIC, expected_guests BIGINT) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        SUM(total_value) AS total_revenue,
        COUNT(DISTINCT client_id) AS expected_guests
    FROM "reserves.reservation"
    WHERE status = 'C'; -- Only confirmed reservations
END;
$$ LANGUAGE plpgsql;

-- FUNCTION TO GET THE TOP PLACEMENTS SECTION IN DASHBOARD
CREATE OR REPLACE FUNCTION get_top_placements()
RETURNS TABLE(city VARCHAR, revenue NUMERIC) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        h.city,
        SUM(r.total_value) AS revenue
    FROM "reserves.reservation" r
    JOIN "reserves.room_reservation" rr ON r.id = rr.reservation_id
    JOIN "room_management.room" rm ON rr.room_id = rm.id
    JOIN "management.hotel" h ON rm.hotel_id = h.id
    GROUP BY h.city
    ORDER BY revenue DESC
    LIMIT 5;
END;
$$ LANGUAGE plpgsql;

-- FUNCTION TO GET THE SALES OVERTIME SECTION IN DASHBOARD
CREATE OR REPLACE FUNCTION get_sales_over_time()
RETURNS TABLE(day INTEGER, revenue NUMERIC) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        EXTRACT(DAY FROM r.begin_date)::INTEGER AS day,
        SUM(r.total_value) AS revenue
    FROM "reserves.reservation" r
    WHERE r.begin_date >= DATE_TRUNC('month', CURRENT_DATE)
    GROUP BY day
    ORDER BY day;
END;
$$ LANGUAGE plpgsql;

