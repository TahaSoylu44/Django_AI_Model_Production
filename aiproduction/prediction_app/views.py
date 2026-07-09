from django.views.generic import FormView, DetailView, ListView
from django.shortcuts import redirect
from .forms import TripPredictionForm, ShowLocationsBasedOnDate, DriverForm
from .models import Historical, Prediction, Location, DriverEntry
from .preprocessing import build_dataframe, get_int_taxi_count
from django.apps import apps
import lightgbm as lgb
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.contrib import messages

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)    # HTML'e giden dict
        current_prediction = self.get_object()  # yakalan prediction objesi

        historical_record = Historical.objects.filter(  # aynı tarih ve saatlisini bul.
            pulocation=current_prediction.pulocation,
            datetime=current_prediction.datetime
        ).first()

        context["record"] = historical_record
        return context
    
    #! normalde biz redirect ile bu class içerisine girdiğimizde elimizde sadece
    #! tahmin verisi vardı. Ama ben bu tahmin verisini gerçek değer ile karşılaştırmak
    #! istediğimden "get_context_data" fonksiyonunu override edip "record" historical
    #! objesini de HTML'e göndereceğim.

class GeneralHistoricalView(ListView):
    model = Historical
    template_name = "prediction_app/general_historical_template.html"
    context_object_name = "records"

    paginate_by = 50    # 50 şer 50 şer göster sayfa 
    
    def dispatch(self, request, *args, **kwargs):   # Request geldiğinde ilk çalışan fonksiyonda, Database'e bulaşmadan ID check yaptım.
        location_id = self.kwargs.get('pk')

        if location_id < 1 or location_id > 265:
            return render(self.request, "prediction_app/over_location.html", {"requested_id": location_id})
        
        return super().dispatch(request, *args, **kwargs)   # Her şey yolunda devam et.

    def get_queryset(self):
        # URL'den gelen 'pk' değerini yakala
        location_id = self.kwargs.get('pk')
        
        # Eğer bu ID'ye sahip bir lokasyon yoksa 404 dön.
        self.location_object = get_object_or_404(Location, pk=location_id)

        # Sadece bu lokasyona ait verileri tarihleri sıralayarak getir.
        return Historical.objects.filter(pulocation=self.location_object).order_by('-datetime')
         
    def get_context_data(self, **kwargs):
        # Lokasyon objesini de ekleyelim
        context = super().get_context_data(**kwargs)
        context['location'] = self.location_object
        return context

def blank_historical_page(request):
    """If user does not enter a location ID, displays this function."""
    return render(request, "prediction_app/blank_location.html")


class Date(FormView):
    template_name = "prediction_app/date.html"
    form_class = ShowLocationsBasedOnDate   # Hangi form class beni doğruluyor?

    def form_valid(self, form):
        target_date = form.cleaned_data["target_datetime"]
        target_date = target_date.replace(minute=0, second=0, microsecond=0)    # verimiz tam saatler üzerine kurulu
        records = Historical.objects.filter(datetime=target_date).select_related('pulocation').order_by('-trip_count')  # SQL JOIN

        if not records.exists():
            form.add_error(None, "Please select a date between 2015-2016")
            return self.form_invalid(form)
        
        context = self.get_context_data(form=form)
        context["records"] = records
        context["target_date"] = target_date

        return self.render_to_response(context)
    
class Entry(FormView):
    template_name = "prediction_app/new_entry.html"
    form_class = DriverForm

    success_url = reverse_lazy('prediction_app:home')   # form kaydedildikten sonra kullanıcının gideceği ekran

    def form_valid(self, form):
        driver_name = form.cleaned_data["driver_name"]
        passenger_count = form.cleaned_data["passenger_count"]
        pulocation = form.cleaned_data["location"]
        datetime = form.cleaned_data["datetime"]

        new_driver_entry = DriverEntry(
            pulocation=pulocation,
            datetime=datetime,
            driver_name=driver_name,
            passenger_count=passenger_count
        )

        new_driver_entry.save() # veri tabanına kaydet, signal çalıştır.
        formatted_date = datetime.strftime("%B %d, %Y - %H:%M") # print attığımızda güzel gözüksün.
        messages.success(self.request, f"Trip recorded successfully for {driver_name} on {formatted_date}")
        return super().form_valid(form)