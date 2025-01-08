INSERT INTO "room_management.room_types" (TYPE_INITIALS, ROOM_VIEW, ROOM_QUALITY)
VALUES 
    ('STD', 'N'::"room_view_type", 'B'::"room_quality_type"),  
    ('DLX', 'P'::"room_view_type", 'S'::"room_quality_type"),  
    ('PRM', 'M'::"room_view_type", 'S'::"room_quality_type"),  
    ('FAM', 'S'::"room_view_type", 'B'::"room_quality_type"),  
    ('ECO', 'N'::"room_view_type", 'B'::"room_quality_type");
