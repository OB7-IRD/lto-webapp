from django.apps import AppConfig


class WebappsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'webapps'

    def ready(self):
        import webapps.signals  # Importer les signaux pour les connecter
