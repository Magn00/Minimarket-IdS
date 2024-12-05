from django.shortcuts import render
from functools import wraps

def role_required(role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated or request.user.rol != role:

                return render(request, 'core/403.html', status=403)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator