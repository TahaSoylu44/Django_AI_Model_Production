from django.views.generic import FormView, DetailView, ListView, DeleteView, UpdateView
from django.shortcuts import redirect
from django.apps import apps
import lightgbm as lgb
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from prediction_app.forms import TripPredictionForm, ShowLocationsBasedOnDate, DriverForm
from prediction_app.models import Historical, Prediction, Location, DriverEntry
from prediction_app.preprocessing import build_dataframe, get_int_taxi_count
from prediction_app.services import reconstruct_pipeline
from django.db import transaction
from django.db.models import F

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
    
class Entry(LoginRequiredMixin, FormView):
    template_name = "prediction_app/new_entry.html"
    form_class = DriverForm
    login_url = "/login/"

    success_url = reverse_lazy('prediction_app:home')   # form kaydedildikten sonra kullanıcının gideceği ekran

    def form_valid(self, form):
        passenger_count = form.cleaned_data["passenger_count"]

        if passenger_count == 0:
            form.add_error("passenger_count", "The passenger count cannot be 0")
            return self.form_invalid(form)
        elif passenger_count > 6:
            form.add_error("passenger_count", "The passenger count cannot be more than 6")
            return self.form_invalid(form)

        pulocation = form.cleaned_data["location"]
        datetime = form.cleaned_data["datetime"]

        new_driver_entry = DriverEntry(
            pulocation=pulocation,
            datetime=datetime,
            driver=self.request.user,
            passenger_count=passenger_count
        )

        new_driver_entry.save() # veri tabanına kaydet, signal çalıştır.
        formatted_date = datetime.strftime("%B %d, %Y - %H:%M") # print attığımızda güzel gözüksün.
        messages.success(self.request, f"Trip recorded successfully for {self.request.user.username} on {formatted_date}")
        return super().form_valid(form)
    
class DeleteDriverEntry(LoginRequiredMixin, DeleteView):
    model = DriverEntry
    success_url = reverse_lazy("list_user_log")
    login_url = "/login/"

    def get_queryset(self):
        return self.request.user.logs.order_by("-created_at")
    
    def form_valid(self, form): # form_class = BaseDeleteView
        messages.success(self.request, "The entry deleted successfully")
        return super().form_valid(form)
    
class UpdateDriverEntry(LoginRequiredMixin, UpdateView):
    template_name = "prediction_app/update_entry.html"
    model = DriverEntry
    success_url = reverse_lazy("list_user_log")
    login_url = "/login/"
    fields = ["pulocation", "datetime", "passenger_count"]

    def get_queryset(self):
        return self.request.user.logs.order_by("-created_at")

    def form_valid(self, form):
        passenger_count = form.cleaned_data["passenger_count"]

        if passenger_count == 0:
            self.object.delete()
            messages.warning(self.request, message="The passenger_count set to 0, the entry deleted!")
            return redirect("list_user_log")
        elif passenger_count > 6:
            form.add_error("passenger_count", "The passenger count cannot be more than 6")
            return self.form_invalid(form)
        else:
            old_entry = get_object_or_404(DriverEntry, pk=self.object.pk)
            old_location = old_entry.pulocation
            old_datetime = old_entry.datetime

            new_location = form.cleaned_data["pulocation"]
            new_datetime = form.cleaned_data["datetime"]
            new_datetime_modified = new_datetime.replace(minute=0, second=0, microsecond=0)

            with transaction.atomic():  # database consistency
                if (old_location != new_location) or (old_datetime != new_datetime_modified):    # Lokasyon veya Tarih değişti.
                    old_historical = get_object_or_404(Historical, pulocation=old_location, datetime=old_datetime.replace(minute=0, second=0, microsecond=0))

                    if old_historical.trip_count > 0:
                        old_historical.trip_count = F("trip_count") - 1  # Eski kayıt 1 azaltıldı. SQL Level, for multi user applications
                        old_historical.save()

                        reconstruct_pipeline(location_object=old_location, updated_datetime=old_datetime)

                    new_entry = get_object_or_404(Historical, pulocation=new_location, datetime=new_datetime_modified)

                    new_entry.trip_count = F("trip_count") + 1   # Yeni kayıt 1 arttırıldı. SQL Level, for multi user applications
                    new_entry.save()
                    reconstruct_pipeline(location_object=new_location, updated_datetime=new_datetime_modified)

            messages.success(self.request, "The entry updated successfully")
            return super().form_valid(form)