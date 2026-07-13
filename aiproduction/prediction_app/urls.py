from django.urls import path
from prediction_app.views import trip

app_name = "prediction_app"

urlpatterns = [
    path("", trip.Home.as_view(), name="home"),
    path("train/<int:pk>/", trip.HistoricalDetailView.as_view(), name="historical_detail"),
    path("test/<int:pk>/", trip.PredictionDetailView.as_view(), name="prediction_detail"),
    path("location/<int:pk>/", trip.GeneralHistoricalView.as_view(), name="general_historical_view"),
    path("location/", trip.blank_historical_page, name="blank_historical"),
    path("date/", trip.Date.as_view(), name="date"),
    path("entry/", trip.Entry.as_view(), name="entry")
]