from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import DriverEntry, Historical
from .services import reconstruct_pipeline

@receiver(post_save, sender=DriverEntry)    # eğer yeni bir DriverEntry .save() edilirse otomatik çalış!
def update_historical_feature(sender, instance, created, **kwargs):
    """When a new entry occurs, updates the timeseries features."""
    if created:
        target_datetime = instance.datetime.replace(minute=0, second=0, microsecond=0)

        historical_record, is_new = Historical.objects.get_or_create(
            pulocation=instance.pulocation,
            datetime=target_datetime,
            defaults={"trip_count": 0}
        )

        historical_record.trip_count += 1
        historical_record.save()

        reconstruct_pipeline(location_object=instance.pulocation, updated_datetime=target_datetime)