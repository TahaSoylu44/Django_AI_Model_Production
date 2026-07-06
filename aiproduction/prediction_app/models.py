from django.db import models

class TaxiTripFeature(models.Model):
    datetime = models.DateTimeField(db_index=True)  #* db_index=True fast look-up sağlar.
    pulocation_id = models.IntegerField(db_index=True)
    is_train = models.BooleanField(default=True)
    actual_trip_count = models.FloatField(null=True, blank=True)    # sadece train verisi için
    # To make a FloatField accept empty or missing values in Django, you should almost always set both null=True and blank=True

    #! Database den hızlıca çekilmesi gereken veriler.
    lag_24h = models.FloatField()
    lag_168h = models.FloatField()
    rolling_mean_3h = models.FloatField()
    rolling_std_12h = models.FloatField()
    ewm_12h = models.FloatField()

    class Meta:
        unique_together = ('datetime', 'pulocation_id') # ignore conflicts tarafından kullanılır.
