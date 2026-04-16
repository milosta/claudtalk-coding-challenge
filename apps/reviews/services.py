from django.core.cache import cache
from django.db.models import Avg, Count

from .models import Review

CACHE_KEY = "product:agg:{pk}"
CACHE_TTL = 3600


def _compute_aggregate(product_id: int) -> dict:
    data = Review.objects.filter(product_id=product_id).aggregate(
        avg=Avg("rating"),
        count=Count("id"),
    )
    return {
        "avg": float(data["avg"]) if data["avg"] is not None else None,
        "count": data["count"] or 0,
    }


def get_product_aggregate(product_id: int) -> dict:
    """Return {"avg": float | None, "count": int} for a product, cached in Redis."""
    return cache.get_or_set(
        CACHE_KEY.format(pk=product_id),
        lambda: _compute_aggregate(product_id),
        CACHE_TTL,
    )


def invalidate_aggregate(product_id: int) -> None:
    cache.delete(CACHE_KEY.format(pk=product_id))
