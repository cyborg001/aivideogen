from django.apps import AppConfig


class ResearcherConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'researcher'
    
    def ready(self):
        """Importar signals para activar auto-limpieza de categorías"""
        import researcher.signals
