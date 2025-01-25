# decorators.py
from functools import wraps
from django.core.exceptions import PermissionDenied

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if request.user.role.id in allowed_roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return wrapped
    return decorator