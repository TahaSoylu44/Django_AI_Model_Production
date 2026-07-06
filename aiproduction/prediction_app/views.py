import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import TaxiTripFeature
from .apps import PredictionAppConfig
from .preprocessing import build_dataframe, get_int_taxi_count

@csrf_exempt    # CSRF kalkanını kapat 
def predict_trip_count(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)

            request_data = {    # user tarafından sağlanan veri ile bir dict oluşturdum.
                "datetime": body.get("datetime"),
                "PULocationID": body.get("PULocationID")
            }

            db_record = TaxiTripFeature.objects.filter(
                datetime=request_data["datetime"],
                pulocation_id=request_data["PULocationID"]
            ).first()   # database'de veri varsa al yoksa None dön!

            if not db_record:
                return JsonResponse({
                    "status": "ERROR!",
                    "message": "Enter a valid range 2015-2016"
                }, status=404)
            
            if db_record.is_train:  # Train verisi
                return JsonResponse({
                    "status": "SUCCESS",
                    "message": "The data belongs to the training set. The actual values are listed.",
                    "actual_trip_count": db_record.actual_trip_count
                })
            
            else:   # Test Verisi
                historical_stats = {
                    "lag_24h": db_record.lag_24h,
                    "lag_168h": db_record.lag_168h,
                    "rolling_mean_3h": db_record.rolling_mean_3h,
                    "rolling_std_12h": db_record.rolling_std_12h,
                    "ewm_12h": db_record.ewm_12h
                }

                #! PREDICTION
                final_df = build_dataframe(request_data, historical_stats)
                prediction_array = PredictionAppConfig.model.predict(final_df)
                prediction_value = get_int_taxi_count(float(prediction_array[0]))

                return JsonResponse({
                    "status": "SUCCESS",
                    "message": "The prediction was calculated.",
                    "predicted_trip_count": prediction_value,
                    "actual_trip_count": db_record.actual_trip_count                    
                })

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"state": "ERROR!", "message": "Only POST accepted"}, status=405)