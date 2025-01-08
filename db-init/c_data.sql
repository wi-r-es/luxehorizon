INSERT INTO "ROOM_MANAGEMENT.ROOM_TYPES" (TYPE_INITIALS, ROOM_VIEW, ROOM_QUALITY)
VALUES 
    ('STD', 'N'::"ROOM_MANAGEMENT.room_view_type", 'B'::"ROOM_MANAGEMENT.room_quality_type"),  
    ('DLX', 'P'::"ROOM_MANAGEMENT.room_view_type", 'S'::"ROOM_MANAGEMENT.room_quality_type"),  
    ('PRM', 'M'::"ROOM_MANAGEMENT.room_view_type", 'S'::"ROOM_MANAGEMENT.room_quality_type"),  
    ('FAM', 'S'::"ROOM_MANAGEMENT.room_view_type", 'B'::"ROOM_MANAGEMENT.room_quality_type"),  
    ('ECO', 'N'::"ROOM_MANAGEMENT.room_view_type", 'B'::"ROOM_MANAGEMENT.room_quality_type");
