INSERT INTO "room_management.room_types" (TYPE_INITIALS, ROOM_VIEW, ROOM_QUALITY)
VALUES 
    ('STD', 'N'::"room_management.room_view_type", 'B'::"room_management.room_quality_type"),  
    ('DLX', 'P'::"room_management.room_view_type", 'S'::"room_management.room_quality_type"),  
    ('PRM', 'M'::"room_management.room_view_type", 'S'::"room_management.room_quality_type"),  
    ('FAM', 'S'::"room_management.room_view_type", 'B'::"room_management.room_quality_type"),  
    ('ECO', 'N'::"room_management.room_view_type", 'B'::"room_management.room_quality_type");
