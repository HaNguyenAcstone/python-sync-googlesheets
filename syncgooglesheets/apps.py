from django.apps import AppConfig

class SyncgooglesheetsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'syncgooglesheets'

    def ready(self):
        print('start scheduling...')
        from .sync_scheduler import sync_googlesheet
        sync_googlesheet.start()
     