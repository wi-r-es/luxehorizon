import random
from utils.hotels import hotels
from utils.funcs import safe_execute
# Room configurations
room_configs = {
    'views': {
        'CITY': 'C',
        'OCEAN': 'O',
        'GARDEN': 'G',
        'POOL': 'P',
        'MOUNTAIN': 'M',
    },
    'qualities': {
        'STANDARD': 'S',
        'DELUXE': 'D',
        'PREMIUM': 'P',
    },
    'capacity': {
        'SINGLE': 'S',
        'DOUBLE': 'D',
        'TRIPLE': 'T',
        'QUAD': 'Q',
        'KING': 'K',
        'FAMILY': 'F',
        'PENTHOUSE': 'P',
    },
}

# Base price dictionary
base_prices = {
    'views': {
        'CITY': 100,
        'OCEAN': 150,
        'GARDEN': 120,
        'POOL': 150,
        'MOUNTAIN': 130,
    },
    'qualities': {
        'STANDARD': 0,
        'DELUXE': 150,
        'PREMIUM': 300,
    },
    'capacity': {
        'SINGLE': 0,
        'DOUBLE': 30,
        'TRIPLE': 50,
        'QUAD': 100,
        'KING': 150,
        'FAMILY': 250,
        'PENTHOUSE': 500,
    },
}



def create_rooms(cursor, self):

    # Add rooms with random configurations
    for hotel_id in range(1, 6):  # For each hotel
        for _ in range(10):  # Create 10 rooms per hotel
            # Generate random room configurations
            view_full_name, view_code = random.choice(list(room_configs['views'].items()))
            quality_full_name, quality_code = random.choice(list(room_configs['qualities'].items()))
            capacity_full_name, capacity_code = random.choice(list(room_configs['capacity'].items()))
            type_initials = f"{view_code}{quality_code}{capacity_code}"

            # Calculate the base price based on configurations
            base_price = (
                base_prices['views'][view_full_name] +
                base_prices['qualities'][quality_full_name] +
                base_prices['capacity'][capacity_full_name]
            )

            # Generate random room number
            room_number = random.randint(100, 500)

            # Insert the room
            safe_execute(
                cursor,
                f"""
                CALL sp_add_room(
                    {hotel_id},        -- Hotel ID
                    '{type_initials}', -- Type initials
                    {room_number},     -- Room number
                    {base_price:.2f},  -- Base price
                    0                  -- Initial condition (Available)
                );
                """,
                success_message=f"Added Room: Hotel {hotel_id}, Type {type_initials}, Room {room_number}, Price {base_price:.2f}",
                error_message=f"Error adding room {hotel_id} for hotel {room_number}"
                )
            #self.stdout.write(f"Added Room: Hotel {hotel_id}, Type {type_initials}, Room {room_number}, Price {base_price:.2f}")    
