def generate_invoices(cursor, self):
    # Fetch all paid reservations with status 'C'
    cursor.execute('SELECT id FROM "reserves.reservation" WHERE status = \'P\' ;')
    pending_R = cursor.fetchall()

    # Flatten the list of tuples into a list of integers
    reservation_ids = [row[0] for row in pending_R]
    self.stdout.write(f"Selected Reservation IDs: {reservation_ids}.")
    _invID =''
    # Generate invoices for these reservations
    for reservation_id in reservation_ids:
        cursor.execute(f"""
            DO $$
            DECLARE
                _invID INT;
            BEGIN
                CALL sp_generate_invoice({reservation_id}, 1, _invID);
                RAISE NOTICE 'Generated Invoice ID: %', _invID;
            END $$;
        """)
        self.stdout.write(f"Generated invoice {_invID} for reservation ID {reservation_id}.")
