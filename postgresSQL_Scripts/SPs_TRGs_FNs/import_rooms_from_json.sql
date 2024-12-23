/* Função que importa quartos de um JSON */
CREATE OR REPLACE FUNCTION ROOM_MANAGEMENT.import_rooms(hotel_id INT, rooms_json JSONB)
RETURNS VOID AS $$
DECLARE
    room JSONB; -- Change `room` to JSONB type
BEGIN
    -- Iterate over the array of rooms
    FOR room IN SELECT jsonb_array_elements(rooms_json) -- Extract JSONB elements
    LOOP
        -- Insert the room into the database
        INSERT INTO ROOM_MANAGEMENT.room (
            type_id, hotel_id, room_number, base_price, condition, capacity
        )
        VALUES (
            (SELECT id FROM ROOM_MANAGEMENT.room_types WHERE type_initials = room->>'type_initials' LIMIT 1),
            hotel_id,
            (room->>'room_number')::INT,
            (room->>'base_price')::NUMERIC,
            (room->>'condition')::INT,
            (room->>'capacity')::TEXT -- Cast explicitly if necessary
        )
        ON CONFLICT (hotel_id, room_number) DO NOTHING; -- Avoid inserting duplicate rooms
    END LOOP;
END;
$$ LANGUAGE plpgsql;
