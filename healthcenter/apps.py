import sys
from django.apps import AppConfig

class HealthcenterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'healthcenter'

    def ready(self):
        import healthcenter.signals

        # Only start the scheduler when running the server
        if 'runserver' in sys.argv or 'runworker' in sys.argv:
            from healthcenter.scheduler import start
            start()
