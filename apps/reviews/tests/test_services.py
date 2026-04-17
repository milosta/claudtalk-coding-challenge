from django.core.cache import cache
from django.test import TestCase

from apps.catalog.tests.factories import ProductFactory
from apps.reviews.services import CACHE_KEY, get_product_aggregate, invalidate_aggregate
from apps.reviews.tests.factories import ReviewFactory


class ProductAggregateTest(TestCase):
    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_aggregate_empty(self):
        product = ProductFactory()
        agg = get_product_aggregate(product.pk)
        self.assertIsNone(agg["avg"])
        self.assertEqual(agg["count"], 0)

    def test_aggregate_with_reviews(self):
        product = ProductFactory()
        ReviewFactory(product=product, rating=4)
        ReviewFactory(product=product, rating=2)
        agg = get_product_aggregate(product.pk)
        self.assertEqual(agg["avg"], 3.0)
        self.assertEqual(agg["count"], 2)

    def test_aggregate_is_cached(self):
        product = ProductFactory()
        ReviewFactory(product=product, rating=5)
        get_product_aggregate(product.pk)
        self.assertIsNotNone(cache.get(CACHE_KEY.format(pk=product.pk)))

    def test_signal_invalidates_on_create(self):
        product = ProductFactory()
        get_product_aggregate(product.pk)
        self.assertIsNotNone(cache.get(CACHE_KEY.format(pk=product.pk)))
        ReviewFactory(product=product, rating=3)
        self.assertIsNone(cache.get(CACHE_KEY.format(pk=product.pk)))

    def test_signal_invalidates_on_delete(self):
        product = ProductFactory()
        review = ReviewFactory(product=product, rating=5)
        get_product_aggregate(product.pk)
        self.assertIsNotNone(cache.get(CACHE_KEY.format(pk=product.pk)))
        review.delete()
        self.assertIsNone(cache.get(CACHE_KEY.format(pk=product.pk)))

    def test_invalidate_helper(self):
        product = ProductFactory()
        ReviewFactory(product=product, rating=4)
        get_product_aggregate(product.pk)
        invalidate_aggregate(product.pk)
        self.assertIsNone(cache.get(CACHE_KEY.format(pk=product.pk)))
