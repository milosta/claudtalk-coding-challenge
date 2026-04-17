from django.test import TestCase

from apps.catalog.tests.factories import CategoryFactory, ProductFactory
from apps.reviews.tests.factories import ReviewFactory


class ProductListTest(TestCase):
    def test_list_page_loads(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)

    def test_filter_by_category(self):
        cat_a = CategoryFactory(name="Audio", slug="audio")
        cat_b = CategoryFactory(name="Video", slug="video")
        ProductFactory(name="Headphones X", category=cat_a)
        ProductFactory(name="Camera Y", category=cat_b)
        resp = self.client.get(f"/?category={cat_a.pk}")
        content = resp.content.decode()
        self.assertIn("Headphones X", content)
        self.assertNotIn("Camera Y", content)

    def test_filter_by_min_rating(self):
        p_high = ProductFactory(name="Top Rated")
        p_low = ProductFactory(name="Low Rated")
        for _ in range(3):
            ReviewFactory(product=p_high, rating=5)
        ReviewFactory(product=p_low, rating=1)
        resp = self.client.get("/?min_rating=4")
        content = resp.content.decode()
        self.assertIn("Top Rated", content)
        self.assertNotIn("Low Rated", content)

    def test_sort_by_name(self):
        ProductFactory(name="Zebra Speaker")
        ProductFactory(name="Alpha Mic")
        resp = self.client.get("/?sort=name")
        content = resp.content.decode()
        alpha_pos = content.index("Alpha Mic")
        zebra_pos = content.index("Zebra Speaker")
        self.assertLess(alpha_pos, zebra_pos)

    def test_htmx_returns_partial(self):
        resp = self.client.get("/", headers={"HX-Request": "true"})
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode()
        self.assertIn('id="product-grid"', content)
        self.assertNotIn("<html", content)


class ProductDetailTest(TestCase):
    def test_detail_page_loads(self):
        product = ProductFactory()
        resp = self.client.get(f"/{product.slug}/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(product.name, resp.content.decode())

    def test_detail_shows_reviews(self):
        product = ProductFactory()
        ReviewFactory(product=product, title="Great gadget")
        resp = self.client.get(f"/{product.slug}/")
        self.assertIn("Great gadget", resp.content.decode())


class ProductSearchTest(TestCase):
    def test_search_returns_matching(self):
        ProductFactory(name="Wireless Headphones", description="Great audio")
        ProductFactory(name="USB Camera", description="HD video")
        resp = self.client.get("/?q=headphones")
        content = resp.content.decode()
        self.assertIn("Wireless Headphones", content)
        self.assertNotIn("USB Camera", content)

    def test_search_empty_query_returns_all(self):
        ProductFactory(name="Product A")
        ProductFactory(name="Product B")
        resp = self.client.get("/?q=")
        content = resp.content.decode()
        self.assertIn("Product A", content)
        self.assertIn("Product B", content)
