import pandas as pd
import numpy as np

def build_dataframe(request_data: dict, historical_data: dict) -> pd.DataFrame:
    """Get the user data and create a new dataframe which can be used by ai model to predict."""

    df = pd.DataFrame([request_data])   # tek satır

    # Hour and Days
    datetime = pd.to_datetime(df["datetime"])
    hour = datetime.dt.hour.values[0]
    day_of_week = datetime.dt.dayofweek.values[0]
    month = datetime.dt.month.values[0]

    is_weekdays = int(day_of_week < 5)
    is_weekend = int(day_of_week >= 5)

    friday_night = (day_of_week == 4) and (hour >= 22)
    saturday = (day_of_week == 5) and ((hour >= 22) or (hour <= 3))
    sunday_night = (day_of_week == 6) and (hour <= 3)
    is_night_life = int(friday_night or saturday or sunday_night)

    is_morning_rush = int((7 <= hour <= 9) and is_weekdays)
    is_evening_rush = int((17 <= hour <= 19) and is_weekdays)
    is_midday_break = int((11 <= hour <= 13) and is_weekdays)

    spring_boolean = int((month == 3) or (month == 4) or (month == 5))
    summer_boolean = int((month == 6) or (month == 7) or (month == 8))
    fall_boolean = int((month == 9) or (month == 10) or (month == 11))
    winter_boolean = int((month == 12) or (month == 1) or (month == 2))
    season = None

    if spring_boolean:
        season = 0
    if summer_boolean:
        season = 1
    if fall_boolean:
        season = 2
    if winter_boolean:
        season = 3

    #! Cycle Encoding 
    hour_sin = np.sin(2 * np.pi * hour / 24)
    hour_cos = np.cos(2 * np.pi * hour / 24)
    day_of_week_sin = np.sin(2 * np.pi * day_of_week / 7)
    day_of_week_cos = np.cos(2 * np.pi * day_of_week / 7)
    seasons_sin = np.sin(2 * np.pi * season / 4)

    pulocation = df["PULocationID"].values[0].pulocation_id
    pulocation_new = 250 if pulocation > 250 else pulocation

    feature_df = {
        "is_weekdays": is_weekdays,
        "is_weekend": is_weekend,
        "is_night_life": is_night_life,
        "is_morning_rush": is_morning_rush,
        "is_evening_rush": is_evening_rush,
        "is_midday_break": is_midday_break,
        "hour_sin": hour_sin,
        "hour_cos": hour_cos,
        "day_of_week_sin": day_of_week_sin,
        "day_of_week_cos": day_of_week_cos,
        "seasons_sin": seasons_sin,
        "lag_24h": historical_data.get("lag_24h", 0),   # eğer değeri veri tabanında bulursan onu al, yoksa 0 de!
        "rolling_std_12h": historical_data.get("rolling_std_12h", 0),
        "PULocationID": pulocation_new,
        "rollin_mean_3h": historical_data.get("rolling_mean_3h", 0),
        "lag_168h": historical_data.get("lag_168h", 0),
        "ewm_12h": historical_data.get("ewm_12h", 0)
    }

    df_final = pd.DataFrame([feature_df])

    df_final = df_final.astype("float32")
    df_final["PULocationID"] = df_final["PULocationID"].astype("int32")

    return df_final


def get_int_taxi_count(count: float) -> int:
    """Get the integer version of the float taxi count."""
    if count < 0:
        return 0
    
    int_value = int(count)

    if count >= int_value + 0.5:
        return int_value + 1
    else:
        return int_value