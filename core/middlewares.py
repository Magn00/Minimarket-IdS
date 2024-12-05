from django.shortcuts import redirect
from django.contrib import messages

class RoleRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Puedes definir permisos específicos según la vista
        role_required = view_kwargs.pop('role_required', None)

        if role_required and request.user.is_authenticated:
            if request.user.rol not in role_required:
                messages.error(request, "No tienes permisos para acceder a esta página.")
                return redirect('lista_productos')  # Redirige a una página segura
        return None