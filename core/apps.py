from django.apps import AppConfig
import threading

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        from core.jobs import start  # Importa dentro del método ready()
        threading.Thread(target=start).start()