from django.apps import AppConfig

class Garden_backendConfig(AppConfig):
    name = 'garden_backend'
    def ready(self):
        import garden_backend.signals