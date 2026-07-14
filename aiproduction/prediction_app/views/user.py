from django.views.generic import FormView, ListView, DeleteView
from prediction_app.forms.user_based import RegisterForm, DeleteUserForm
import lightgbm as lgb
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from prediction_app.models.trip_based import DriverEntry
from prediction_app.permissions import AdminCanAccess
from prediction_app.models.user_based import Taxi_Driver

class UserRegistration(FormView):
    template_name = "prediction_app/register.html"
    form_class = RegisterForm

    success_url = reverse_lazy('prediction_app:home')   # form kaydedildikten sonra kullanıcının gideceği ekran

    def form_valid(self, form):
        user_name = form.cleaned_data["username"]
        name = form.cleaned_data["name"]
        surname = form.cleaned_data["surname"]
        mail = form.cleaned_data["mail"]
        password = form.cleaned_data["password"]

        new_user = User.objects.create_user( # yeni kullanıcı oluştur.
            username=user_name,
            first_name=name,
            last_name=surname,
            email=mail,
            password=password
        )

        login(self.request, new_user)   # kullanıcı başarıyla oluşturulursa sisteme girsin.
        messages.success(self.request, f"You successfully registered {user_name}")
        return super().form_valid(form)
    
class DeleteUser(LoginRequiredMixin, FormView):
    template_name = "prediction_app/delete_user.html"
    success_url = reverse_lazy('prediction_app:home')
    form_class = DeleteUserForm
    login_url = "/login/"

    def form_valid(self, form):
        user = self.request.user
        logout(self.request)
        user.delete()

        messages.success(self.request, "The account successfully deleted.")
        return super().form_valid(form)
    
class ListUserLog(LoginRequiredMixin, ListView):
    model = DriverEntry
    template_name = "prediction_app/list_user_log.html"
    context_object_name = "user_log"
    login_url = "/login/"

    paginate_by = 50

    def get_queryset(self):
        return self.request.user.logs.order_by("-created_at")
    
class ListTaxiDriver(AdminCanAccess, LoginRequiredMixin, ListView):
    model = Taxi_Driver
    template_name = "prediction_app/list_taxi_driver.html"
    context_object_name = "driver_list"
    login_url = "/login/"
    paginate_by = 50

    def get_queryset(self):
        return Taxi_Driver.objects.select_related("user").all().order_by("user__username")
    
class DeleteTaxiDriver(AdminCanAccess, LoginRequiredMixin, DeleteView):
    model = Taxi_Driver
    success_url = reverse_lazy("list_taxi_driver")
    login_url = "/login/"

    def get_queryset(self):
        return Taxi_Driver.objects.select_related("user").all().order_by("user__username")
    
    def form_valid(self, form):
        messages.success(self.request, "The taxi driver deleted!")
        return super().form_valid(form)