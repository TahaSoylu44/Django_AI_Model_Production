from django.db import models
from django.contrib.auth.models import User
from prediction_app.models.user_based import Taxi_Driver

class Location(models.Model):
    pulocation_id = models.PositiveIntegerField(primary_key=True)

    def __str__(self):
        return f"Location {self.pulocation_id}"

class Historical(models.Model):
    pulocation = models.ForeignKey(Location, on_delete=models.CASCADE)
    datetime = models.DateTimeField(db_index=True)
    trip_count = models.PositiveIntegerField()
    rollin_mean_3h = models.FloatField()
    rolling_std_12h = models.FloatField()
    lag_24h = models.PositiveIntegerField()
    lag_168h = models.PositiveIntegerField()
    ewm_12h = models.FloatField()
    is_train = models.BooleanField(default=True, db_index=True)

class Prediction(models.Model):
    pulocation = models.ForeignKey(Location, on_delete=models.CASCADE)
    datetime = models.DateTimeField(db_index=True)
    predValue = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)    # Bu tahmin ne zaman çalıştırıldı?
    predictor = models.ForeignKey(User, on_delete=models.CASCADE)

class DriverEntry(models.Model):
    pulocation = models.ForeignKey(Location, on_delete=models.CASCADE)
    datetime = models.DateTimeField(db_index=True)
    passenger_count = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="logs")

    class Meta:
        db_table = "driver_table_entry" # Tablo ismini kendim belirledim

    def __str__(self):
        return f"{self.driver.username} - Location {self.pulocation.pulocation_id} ({self.datetime})"