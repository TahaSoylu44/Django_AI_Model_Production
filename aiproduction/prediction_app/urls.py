from django.urls import path
from . import views

app_name = "prediction_app"

urlpatterns = [
    path("", views.Home.as_view(), name="home"),
    path("train/<int:pk>/", views.HistoricalDetailView.as_view(), name="historical_detail"),
    path("test/<int:pk>/", views.PredictionDetailView.as_view(), name="prediction_detail"),
    path("location/<int:pk>/", views.GeneralHistoricalView.as_view(), name="general_historical_view"),
    path("location/", views.blank_historical_page, name="blank_historical"),
    path("date/", views.Date.as_view(), name="date"),
    path("entry/", views.Entry.as_view(), name="entry")
]