import pandas as pd
from datetime import timedelta
from .models import Historical, Location
import datetime

def reconstruct_pipeline(location_object: Location, updated_datetime: datetime):
    """When the user enters a new data for a specific location, the related datas are updated."""
    fetch_start = updated_datetime - timedelta(hours=168)

    datas = Historical.objects.filter(
        pulocation=location_object,
        datetime__gte=fetch_start   # greater or equal
    ).order_by('datetime')

    if not datas.exists():
        return
    
    df = pd.DataFrame(list(datas.values('id', 'datetime', 'trip_count', 'pulocation')))
    df.set_index('datetime', inplace=True)

    past_request = df.groupby("pulocation")["trip_count"].shift(1)

    df["rollin_mean_3h"] = past_request.rolling(window=3).mean()
    df["rolling_std_12h"] = past_request.rolling(window=12).std()
    df["lag_24h"] = past_request.shift(23)
    df["lag_168h"] = past_request.shift(167)
    df["ewm_12h"] = past_request.groupby(df["pulocation"]).ewm(span=12).mean().reset_index(level=0, drop=True)

    df = df.fillna(0)

    df_to_update = df[df.index >= updated_datetime].reset_index()

    update_list = []

    for index, row in df_to_update.iterrows():
        historical = Historical(id=row['id'])

        historical.rollin_mean_3h = row["rollin_mean_3h"]
        historical.rolling_std_12h = row["rolling_std_12h"]
        historical.lag_24h = row["lag_24h"]
        historical.lag_168h = row["lag_168h"]
        historical.ewm_12h = row["ewm_12h"]

        update_list.append(historical)

    if update_list:
        Historical.objects.bulk_update(update_list, ["rollin_mean_3h", "rolling_std_12h", "lag_24h", "lag_168h", "ewm_12h"])