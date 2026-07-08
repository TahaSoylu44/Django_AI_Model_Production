from django.views.generic import FormView, DetailView
from django.shortcuts import redirect
from .forms import TripPredictionForm
from .models import Historical, Prediction
from .preprocessing import build_dataframe, get_int_taxi_count
from django.apps import apps
import lightgbm as lgb

class Home(FormView):
    template_name = "prediction_app/home.html"
    form_class = TripPredictionForm

    def form_valid(self, form): # eğer gelen request, tanımladığımız form class ile uyumlu ise otomatik çalışır.
        location = form.cleaned_data['location']
        target_date = form.cleaned_data['target_datetime']
        user_name = form.cleaned_data["predictor_name"]

        target_date = target_date.replace(minute=0, second=0, microsecond=0)    # verimiz tam saatler üzerine kurulu

        record = Historical.objects.filter(pulocation=location, datetime=target_date).first()
        #! Eğer böyle bir veri database de varsa al yoksa None dön!

        if not record:  #!
            form.add_error(None, "Please select a date between 2015-2016")
            return self.form_invalid(form)

        #TODO: EĞİTİM VERİSİ
        if record.is_train:
            return redirect('prediction_app:historical_detail', pk=record.pk)
        
        else:   #* Tahmin verisi
            request_data = {
                "datetime": target_date,
                "PULocationID": location
            }

            historical_data = {
                "lag_24h": record.lag_24h,
                "rolling_std_12h": record.rolling_std_12h,
                "rollin_mean_3h": record.rollin_mean_3h,
                "lag_168h": record.lag_168h,
                "ewm_12h": record.ewm_12h
            }

            final_df = build_dataframe(request_data, historical_data)
            app_config = apps.get_app_config('prediction_app')

            prediction_array = app_config.model.predict(final_df)
            prediction = get_int_taxi_count(float(prediction_array[0]))

            prediction_object = Prediction.objects.create(
                pulocation = location,
                datetime = target_date,
                predValue = prediction,
                predictor_name = user_name
            )

            return redirect('prediction_app:prediction_detail', pk=prediction_object.pk)
        

class HistoricalDetailView(DetailView):
    model = Historical
    template_name = "prediction_app/historical_result.html"
    context_object_name = "record"

class PredictionDetailView(DetailView):
    model = Prediction
    template_name = "prediction_app/prediction_result.html"
    context_object_name = "prediction_object"