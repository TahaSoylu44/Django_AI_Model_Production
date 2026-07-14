from django.db import models
from django.contrib.auth.models import User

class Taxi_Driver(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="driver"
    )

    driver_id = models.PositiveIntegerField(primary_key=True)

    def __str__(self):
        return self.user.username

class Admin(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="admin"
    )

    admin_id = models.PositiveIntegerField(primary_key=True)

    def __str__(self):
        return self.user.username