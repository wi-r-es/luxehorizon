import random
from datetime import datetime, timedelta

def create_reservations(cursor, self):
    # Get all client IDs
    cursor.execute('SELECT id FROM "hr.users" WHERE utp = \'C\';')  # Assuming 'C' indicates a client
    client_ids = [row[0] for row in cursor.fetchall()]

    # Get all available room IDs
    cursor.execute('SELECT id FROM "room_management.room" WHERE condition = 0;')  # Assuming 'condition = 0' means available
    room_ids = [row[0] for row in cursor.fetchall()]

    if not room_ids:
        self.stdout.write("No available rooms to create reservations.")
        return

    # Create Reservations
    start_date = datetime.now().date()
    for client_id in client_ids:
        for _ in range(3):  # Retry up to 3 times for each client
            room_id = random.choice(room_ids)  # Random room assignment
            checkin_date = start_date + timedelta(days=random.randint(1, 30))  # Random check-in within the next 30 days
            checkout_date = checkin_date + timedelta(days=random.randint(1, 7))  # Stay duration of 1-7 days
            guest_count = random.randint(1, 4)  # Random number of guests (1-4)

            try:
                # Attempt to create the reservation
                cursor.execute(f"""
                CALL sp_create_reservation(
                    {client_id},              
                    {room_id},                
                    '{checkin_date}',         
                    '{checkout_date}',        
                    {guest_count}             
                );
                """)
                self.stdout.write(f"Created reservation: Client {client_id}, Room {room_id}, Check-in {checkin_date}, Check-out {checkout_date}, Guests {guest_count}")
                break  # Exit the retry loop if successful
            except Exception as e:
                self.stdout.write(f"Failed to create reservation for Client {client_id} with Room {room_id}. Retrying... Error: {e}")
                continue
        else:
            self.stdout.write(f"Failed to create a reservation for Client {client_id} after 3 attempts.")
