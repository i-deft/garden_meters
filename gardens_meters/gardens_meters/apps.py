from django.apps import AppConfig

class Garden_backendConfig(AppConfig):
    name = 'gardens_meters'
    def ready(self):
        import gardens_meters.signals