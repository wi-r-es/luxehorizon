hotels = [
                ('Grand Luxe Hotel', '123 Elm Street', '1234-678', 'Viseu', 5),
                ('Lisboa Premium Suites', '456 Maple Ave', '5678-123', 'Lisboa', 4),
                ('Porto Comfort', '789 Oak Lane', '6789-456', 'Porto', 4),
                ('Algarve Sun Resort', '321 Palm Beach Rd', '8765-432', 'Algarve', 5),
                ('Douro Valley Retreat', '987 Wine St', '3456-789', 'Douro', 5)
        ]

# Commodity list
commodities = [
    "Free WiFi",                                # ID 1
    "Air Conditioning",                         # ID 2
    "Flat-Screen TV",                           # ID 3
    "Minibar",                                  # ID 4
    "Safe",                                     # ID 5
    "Room Service",                             # ID 6
    "Coffee Maker",                             # ID 7
    "Hair Dryer",                               # ID 8
    "Iron and Ironing Board",                   # ID 9
    "Desk and Chair",                           # ID 10
    "Blackout Curtains",                        # ID 11
    "Wooden floor",                             # ID 12
    "Jacuzzi",                                  # ID 13
    "Bathtub",                                  # ID 14,
]

# Room types and their associated commodity IDs
room_commodities = {
    'S': [1, 2, 3, 4, 5, 9],                                       # Basic commodities
    'D': [1, 2, 3, 4, 5, 6, 7, 8, 10],                             # Standard + extras
    'P': [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12],                     # Deluxe + more extras
    'PH': [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14],            # Premium + Jacuzzi
}