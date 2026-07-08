from django.urls import path
from . import views

app_name = "prediction_app"

urlpatterns = [
    path("", views.Home.as_view(), name="home"),
    path("train/<int:pk>/", views.HistoricalDetailView.as_view(), name="historical_detail"),
    path("test/<int:pk>/", views.PredictionDetailView.as_view(), name="prediction_detail"),
]