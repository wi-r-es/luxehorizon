from django.db import models
from django.db.models.fields import NOT_PROVIDED
from django.db import connection

class PostgreSQLEnumField(models.Field):
    def __init__(self, enum_name, choices=None, *args, **kwargs):
        self.enum_name = enum_name
        
        # If choices are not provided, fetch them from the database
        if not choices:
            choices = self._get_enum_choices()
        
        kwargs['choices'] = choices
        super().__init__(*args, **kwargs)

    def _get_enum_choices(self):
        """
        Fetch enum values from PostgreSQL
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT e.enumlabel
                FROM pg_type t
                JOIN pg_enum e ON t.oid = e.enumtypid
                WHERE t.typname = %s
                ORDER BY e.enumsortorder;
            """, [self.enum_name])
            
            enum_values = cursor.fetchall()
            return [(value[0], value[0]) for value in enum_values]

    def db_type(self, connection):
        return self.enum_name

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs['enum_name'] = self.enum_name
        if 'choices' in kwargs:
            del kwargs['choices']
        return name, path, args, kwargs

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return str(value)

    def to_python(self, value):
        if value is None:
            return value
        return str(value)

    def get_prep_value(self, value):
        if value is None:
            return value
        return str(value)