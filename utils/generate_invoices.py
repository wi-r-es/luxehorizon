def generate_invoices(cursor, self):
    # Fetch all paid reservations with status 'C'
    cursor.execute("SELECT id FROM reserves.reservation WHERE status = 'C';")
    paid_reservations = [row[0] for row in cursor.fetchall()]

    # Generate invoices for these reservations
    for reservation_id in paid_reservations:
        cursor.execute(f"CALL sp_generate_invoice({reservation_id}, 1);")
        self.stdout.write(f"Generated invoice for reservation ID {reservation_id}.")
