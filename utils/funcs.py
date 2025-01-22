from django.contrib.auth.hashers import make_password
def hash_password(password):
    return make_password(password)

def safe_execute(cursor, query, params=None, success_message=None, error_message=None):
    """
    Safely executes an SQL query, catching exceptions and logging errors.
    """
    try:
        cursor.execute(query, params or [])
        if success_message:
            print(success_message)
    except Exception as e:
        if error_message:
            print(f"{error_message}: {e}")
        else:
            print(f"Error executing query: {e}")
