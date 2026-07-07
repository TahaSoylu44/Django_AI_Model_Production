from django.db import models

class Location(models.Model):
    pulocation_id = models.IntegerField(primary_key=True)

    def __str__(self):
        return f"Location {self.pulocation_id}"

class Historical(models.Model):
    pulocation = models.ForeignKey(Location, on_delete=models.CASCADE)
    datetime = models.DateTimeField(db_index=True)
    trip_count = models.IntegerField()
    rollin_mean_3h = models.FloatField()
    rolling_std_12h = models.FloatField()
    lag_24h = models.FloatField()
    lag_168h = models.FloatField()
    ewm_12h = models.FloatField()
    is_train = models.BooleanField(default=True, db_index=True)

class Prediction(models.Model):
    pulocation = models.ForeignKey(Location, on_delete=models.CASCADE)
    datetime = models.DateTimeField(db_index=True)
    predValue = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)    # Bu tahmin ne zaman çalıştırıldı?
    is_train = models.BooleanField(default=False, db_index=True)