from django.apps import AppConfig


class InvMngConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "inv_mng"

    def ready(self):
        import inv_mng.signals
