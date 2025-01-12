import random

def add_payments_or_cancel_reservs(cursor, self):
    # Fetch all reservations with their total value
    cursor.execute('SELECT id, total_value FROM "reserves.reservation";')
    reservations = cursor.fetchall()  # List of tuples: (reservation_id, total_value)

    # Process each reservation
    for reservation_id, total_value in reservations:
        action = random.choice(["cancel", "pay"])  # Randomly choose an action

        if action == "cancel":
            # Cancel the reservation
            cursor.execute(f"CALL sp_cancel_reservation({reservation_id});")
            self.stdout.write(f"Cancelled reservation ID {reservation_id}.")
        else:
            # Add a payment
            cursor.execute(f"""
                CALL sp_add_payment(
                    _invoice_id := {reservation_id}, 
                    _payment_amount := {total_value:.2f}, 
                    _payment_method_id := 1
                );
            """)    
            self.stdout.write(f"Added payment for reservation ID {reservation_id}: Amount {total_value:.2f}.")
