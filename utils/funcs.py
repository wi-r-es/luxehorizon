from django.contrib.auth.hashers import make_password
def hash_password(password):
    return make_password(password)