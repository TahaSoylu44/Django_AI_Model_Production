from django.urls import path
from . import views

app_name = "prediction_app"

urlpatterns = [
    path("", views.predict_trip_count, name="predict_trip_count"),
]