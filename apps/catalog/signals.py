from django.contrib.postgres.search import SearchVector
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Product


@receiver(post_save, sender=Product)
def update_product_search_vector(sender, instance: Product, **kwargs) -> None:
    """Populate `search_vector` after a Product is saved.

    Uses .update() so the write bypasses save() and does not re-trigger this signal.
    """
    Product.objects.filter(pk=instance.pk).update(
        search_vector=(
            SearchVector("name", weight="A", config="english")
            + SearchVector("description", weight="B", config="english")
        )
    )
