from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Review
from .services import invalidate_aggregate


@receiver(post_save, sender=Review)
@receiver(post_delete, sender=Review)
def invalidate_product_aggregate(sender, instance: Review, **kwargs) -> None:
    invalidate_aggregate(instance.product_id)
