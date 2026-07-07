import pandas as pd
from django.core.management.base import BaseCommand
from prediction_app.models import Location, Historical

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

        self.stdout.write(self.style.SUCCESS(f"Total {len(df)} rows found."))
        
        #! Location Detection
        self.stdout.write(self.style.WARNING("Locations checking..."))
        unique_ids = df["PULocationID"].unique()    # parquet dosyasındaki lokasyon kodları
        existing_ids = set(Location.objects.values_list('pulocation_id', flat=True))    # databasede olan lokasyon id
        new_locations = []

        for loc_id in unique_ids:
            if loc_id not in existing_ids:
                new_locations.append(Location(pulocation_id=int(loc_id)))

        if new_locations:
            Location.objects.bulk_create(new_locations, ignore_conflicts=True)
            self.stdout.write(self.style.SUCCESS(f"{len(new_locations)} new locations created."))

        location_map = {}   # lokasyon kodu ile lokasyon objesine hızlı erişim

        for location in Location.objects.all():
            location_map.update({location.pulocation_id: location})

        #! Historical Data
        self.stdout.write(self.style.WARNING("Uploading the historical data."))
        instances = []

        for index, row in df.iterrows():
            loc_id = int(row["PULocationID"])
            location = location_map.get(loc_id)

            if not location:
                continue

            flag = True if row["month_index"] <= 23 else False

            instances.append(
                Historical(
                    pulocation = location,
                    datetime = row["pickup_hour"],
                    trip_count = row["trip_count"],
                    rollin_mean_3h = row["rollin_mean_3h"],
                    rolling_std_12h = row["rolling_std_12h"],
                    lag_24h = row["lag_24h"],
                    lag_168h = row["lag_168h"],
                    ewm_12h = row["ewm_12h"],
                    is_train = flag
                )
            )

            if len(instances) >= 10000:
                Historical.objects.bulk_create(instances, ignore_conflicts=True)
                instances = []
                self.stdout.write(f"{index + 1} rows completed.")

        if instances:
            Historical.objects.bulk_create(instances, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS("All datas uploaded to the database!"))