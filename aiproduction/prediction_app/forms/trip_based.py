from django import forms
from prediction_app.models.trip_based import Location
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime
from django.utils.timezone import make_aware

class TripPredictionForm(forms.Form):
    #! ModelChoiceField, veri tabanındaki lokasyonları seçilebilir forma getirir.
    location = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        label="Choose a location",
        empty_label="Please select a Location!"
    )

    target_datetime = forms.DateTimeField(
        label="Date and Hour",

        validators=[
            MinValueValidator(make_aware(datetime.datetime(2015, 1, 1, 0, 0))),
            MaxValueValidator(make_aware(datetime.datetime(2016, 12, 31, 23, 59)))
        ],

        widget=forms.DateTimeInput( # HTML görünüm değiştirir.
            attrs={
                'type': 'datetime-local',
                'min': '2015-01-01T00:00',
                'max': '2016-12-31T23:59'
            }
        )
    )

class ShowLocationsBasedOnDate(forms.Form):
    """User belli bir andaki taxi count karşilaştirmasi isterse dolduracagi form."""
    target_datetime = forms.DateTimeField(
        label="Date and Hour",

        validators=[
            MinValueValidator(make_aware(datetime.datetime(2015, 1, 1, 0, 0))),
            MaxValueValidator(make_aware(datetime.datetime(2016, 12, 31, 23, 59)))
        ],

        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'min': '2015-01-01T00:00',
                'max': '2016-12-31T23:59'
            }
        )
    )

class DriverForm(forms.Form):
    """Taxi sürücüsü tarafindan girilen veriler"""
    passenger_count = forms.IntegerField(
        label="Passenger Count",
        min_value=0
    )

    location = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        label="Choose a location",
        empty_label="Please select a location"
    )

    datetime = forms.DateTimeField(
        label="Date and Hour",

        validators=[
            MinValueValidator(make_aware(datetime.datetime(2015, 1, 1, 0, 0))),
            MaxValueValidator(make_aware(datetime.datetime(2016, 12, 31, 23, 59)))
        ],

        widget=forms.DateTimeInput( # HTML görünüm değiştirir.
            attrs={
                'type': 'datetime-local',
                'min': '2015-01-01T00:00',
                'max': '2016-12-31T23:59'
            }
        )
    )