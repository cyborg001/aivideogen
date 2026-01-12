from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import NewsSource

@receiver(post_delete, sender=NewsSource)
def cleanup_empty_categories(sender, instance, **kwargs):
    """
    Auto-limpieza: Elimina categorías que quedan sin fuentes RSS asociadas.
    Se ejecuta automáticamente cuando se construye el paquete o se elimina una fuente.
    """
    try:
        if instance.category_id: # Usar _id para evitar carga automática si no es necesario
            # Verificar si la categoría aún existe (evitar DoesNotExist durante borrados masivos)
            from .models import Category
            try:
                category = Category.objects.get(id=instance.category_id)
            except Category.DoesNotExist:
                return

            # Verificar si esta era la última fuente de esta categoría
            remaining_sources = NewsSource.objects.filter(category_id=instance.category_id).count()
            if remaining_sources == 0:
                name = category.name
                category.delete()
                print(f"✓ Categoría '{name}' eliminada automáticamente (sin fuentes)")
    except Exception:
        # En borrados masivos o estados inconsistentes, simplemente ignoramos
        pass
