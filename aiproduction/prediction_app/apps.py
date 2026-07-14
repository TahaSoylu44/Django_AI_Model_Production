from django.apps import AppConfig
import joblib
import os
from django.conf import settings
import lightgbm as lgb

class PredictionAppConfig(AppConfig):
    name = 'prediction_app'
    default_auto_field = 'django.db.models.BigAutoField'

    model = None    # modeli tutacağımız değişken

    def ready(self):    # sadece bir kez çalış ve modeli hafızaya al
        model_path = os.path.join(settings.BASE_DIR, 'prediction_app', 'ai_models', 'lgb_model.pkl')
        if os.path.exists(model_path):
            PredictionAppConfig.model = joblib.load(model_path)

        from . import signals  # signals dosyası