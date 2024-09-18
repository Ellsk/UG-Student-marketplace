# users/middleware.py
from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse

class AdminAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Allow access to the admin only for the specific users with correct ID and PIN
        if request.path.startswith('/admin/') and not request.user.is_superuser:
            id_number = request.POST.get('id_number')
            pin = request.POST.get('pin')
            if not self.is_valid_user(request, id_number, pin):
                return redirect(reverse('admin:login'))
        response = self.get_response(request)
        return response

    def is_valid_user(self, request, id_number, pin):
        # Validate ID and PIN (you may want to use a more secure method)
        try:
            user = CustomUser.objects.get(id_number=id_number, pin=pin)
            if user.is_superuser:
                request.user = user
                return True
        except CustomUser.DoesNotExist:
            return False
        return False
