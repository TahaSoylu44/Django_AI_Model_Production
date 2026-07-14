"""
URL configuration for aiproduction project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from prediction_app.views.user import UserRegistration, DeleteUser, ListUserLog, ListTaxiDriver, DeleteTaxiDriver
from prediction_app.views.trip import DeleteDriverEntry, UpdateDriverEntry

urlpatterns = [
    path('admin/', admin.site.urls),
    path("predict/", include("prediction_app.urls")),
    path("login/", auth_views.LoginView.as_view(template_name="prediction_app/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/", UserRegistration.as_view(), name="register"),
    path("delete_account/", DeleteUser.as_view(), name="delete_account"),
    path("list_user_log/", ListUserLog.as_view(), name="list_user_log"),
    path("log/<int:pk>/delete/", DeleteDriverEntry.as_view(), name="delete_log"),
    path("log/<int:pk>/update/", UpdateDriverEntry.as_view(), name="update_log"),
    path("list_taxi_driver/", ListTaxiDriver.as_view(), name="list_taxi_driver"),
    path("driver/<int:pk>/delete/", DeleteTaxiDriver.as_view(), name="delete_driver")
]