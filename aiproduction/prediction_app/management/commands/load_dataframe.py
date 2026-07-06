import pandas as pd
from django.core.management.base import BaseCommand
from prediction_app.models import TaxiTripFeature

class Command(BaseCommand): # python manage.py ile çalıştırılabilir hale gel.
    help = 'Load the dataframe into the database'

    def handle(self, *args, **kwargs):
        file_path = "data/final_base_df.parquet"

        self.stdout.write(self.style.WARNING(f"{file_path} is being proceed..."))

        try:
            df = pd.read_parquet(file_path)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Cannot read the file {e}"))
            return
        
        # veri tabanı hata vermesin diye NaN değer varsa, Python None tipine çevirelim.
        df = df.where(pd.notnull(df), None)

        instances = []

        self.stdout.write(self.style.SUCCESS(f"Total {len(df)} rows found."))

        for index, row in df.iterrows():

            flag = True if row["month_index"] <= 23 else False

            instances.append(
                TaxiTripFeature(
                    datetime=row["pickup_hour"],
                    pulocation_id=row["PULocationID"],
                    is_train=flag,  
                    actual_trip_count=row["trip_count"],
                    lag_24h = row["lag_24h"],
                    lag_168h = row["lag_168h"],
                    rolling_mean_3h = row["rollin_mean_3h"],
                    rolling_std_12h = row["rolling_std_12h"],
                    ewm_12h = row["ewm_12h"]
                )
            )

            if len(instances) >= 10000:
                TaxiTripFeature.objects.bulk_create(instances, ignore_conflicts=True)
                instances = []
                self.stdout.write(f"{index + 1} rows executed.")

        if instances:
            TaxiTripFeature.objects.bulk_create(instances, ignore_conflicts=True)   #! parça parça duplicate engelleyerek db oluştur.

        self.stdout.write(self.style.SUCCESS("All datas uploaded to the database!"))