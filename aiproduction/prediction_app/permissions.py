from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect

class DriverCanAccess(UserPassesTestMixin):
    def test_func(self):
        """Erişimi belirleyen fonksiyon"""
        return hasattr(self.request.user, "driver")
    
    def handle_no_permission(self):
        """Erişim red edilince tetiklenen fonksiyon"""
        messages.error(self.request, "Access Denied: You have to be a taxi driver to access this page!")
        return redirect("prediction_app:home")
    
class AdminCanAccess(UserPassesTestMixin):
    def test_func(self):
        """Erişimi belirleyen fonksiyon"""
        return hasattr(self.request.user, "admin")
    
    def handle_no_permission(self):
        """Erişim red edilince tetiklenen fonksiyon"""
        messages.error(self.request, "Access Denied: You have to be an admin to access this page!")
        return redirect("prediction_app:home")
    
class AdminOrDriverCanAccess(UserPassesTestMixin):
    def test_func(self):
        is_admin = hasattr(self.request.user, "admin")
        is_driver = hasattr(self.request.user, "driver")
        return is_admin or is_driver
    
    def handle_no_permission(self):
        messages.error(self.request, "Access Denied: You have to be an admin or a taxi driver to access this page!")
        return redirect("prediction_app:home")