import random
from utils.funcs import safe_execute

def add_payments_or_cancel_reservs(cursor, self):
    # Fetch all reservations with their total value
    safe_execute(
        cursor,
        'SELECT id, total_value FROM "reserves.reservation";',
        success_message="Fetched reservations successfully.",
        error_message="Failed to fetch reservations."
    )
    reservations = cursor.fetchall()  # List of tuples: (reservation_id, total_value)

    # Validate that payment method ID 1 exists
    safe_execute(
        cursor,
        'SELECT COUNT(*) FROM "finance.payment_method" WHERE id = 1;',
        success_message="Checked for payment method ID 1.",
        error_message="Failed to check for payment method ID 1."
    )
    if cursor.fetchone()[0] == 0:
        self.stdout.write("Payment method ID 1 does not exist. Skipping payment insertion.")
        return

    # Process each reservation
    for reservation_id, total_value in reservations:
        action = random.choice(["cancel", "pay"])  # Randomly choose an action

        if action == "cancel":
            # Cancel the reservation
            safe_execute(
                cursor,
                f"CALL sp_cancel_reservation({reservation_id});",
                success_message=f"Cancelled reservation ID {reservation_id}.",
                error_message=f"Failed to cancel reservation ID {reservation_id}."
            )
            self.stdout.write(f"Cancelled reservation ID {reservation_id}.")
        else:
            # Add a payment
            try:
                safe_execute(
                    cursor,
                    f"""
                    CALL sp_add_payment(
                        _invoice_id := {reservation_id}, 
                        _payment_amount := {total_value:.2f}, 
                        _payment_method_id := 1
                    );
                    """,
                    success_message=f"Added payment for reservation ID {reservation_id}: Amount {total_value:.2f}.",
                    error_message=f"Failed to add payment for reservation ID {reservation_id}."
                )
                self.stdout.write(f"Added payment for reservation ID {reservation_id}: Amount {total_value:.2f}.")
            except Exception as e:
                self.stdout.write(f"Error adding payment for reservation ID {reservation_id}: {e}")

