from django.apps import AppConfig


class SocialMediaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'social_media'
    # def ready(self):
    #     # Import celery app now that Django is mostly ready.
    #     # This initializes Celery and autodiscovers tasks
    #     import social_media_monitoring.celery
