from django.test import TestCase

from apps.accounts.tests.factories import UserFactory
from apps.catalog.tests.factories import ProductFactory
from apps.reviews.models import Review
from apps.reviews.tests.factories import ReviewFactory


class ReviewCreateTest(TestCase):
    def setUp(self):
        self.user = UserFactory(password="testpass")
        self.product = ProductFactory()
        self.client.login(username=self.user.username, password="testpass")

    def test_create_review(self):
        url = f"/products/{self.product.slug}/reviews/"
        resp = self.client.post(url, {"rating": 4, "title": "Great", "body": "Loved it"})
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Review.objects.filter(product=self.product, user=self.user).exists())

    def test_create_review_htmx(self):
        url = f"/products/{self.product.slug}/reviews/"
        resp = self.client.post(
            url,
            {"rating": 5, "title": "Amazing", "body": "Wow"},
            headers={"HX-Request": "true"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Review.objects.filter(product=self.product, user=self.user).exists())

    def test_create_requires_login(self):
        self.client.logout()
        url = f"/products/{self.product.slug}/reviews/"
        resp = self.client.post(url, {"rating": 4, "title": "T", "body": "B"})
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp.url)

    def test_duplicate_review_shows_error(self):
        ReviewFactory(product=self.product, user=self.user)
        url = f"/products/{self.product.slug}/reviews/"
        resp = self.client.post(url, {"rating": 3, "title": "Again", "body": "Dup"})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(Review.objects.filter(product=self.product, user=self.user).count(), 1)


class ReviewEditTest(TestCase):
    def setUp(self):
        self.user = UserFactory(password="testpass")
        self.other_user = UserFactory(password="testpass")
        self.product = ProductFactory()
        self.client.login(username=self.user.username, password="testpass")

    def test_edit_own_review(self):
        review = ReviewFactory(product=self.product, user=self.user)
        resp = self.client.post(
            f"/reviews/{review.pk}/edit/",
            {"rating": 2, "title": "Updated", "body": "Changed"},
        )
        self.assertEqual(resp.status_code, 302)
        review.refresh_from_db()
        self.assertEqual(review.title, "Updated")
        self.assertEqual(review.rating, 2)

    def test_edit_htmx_returns_card_with_oob(self):
        review = ReviewFactory(product=self.product, user=self.user)
        resp = self.client.post(
            f"/reviews/{review.pk}/edit/",
            {"rating": 3, "title": "Edited", "body": "New body"},
            headers={"HX-Request": "true"},
        )
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode()
        self.assertIn(f'id="review-{review.pk}"', content)
        self.assertIn("hx-swap-oob", content)

    def test_edit_htmx_get_shows_inline_form(self):
        review = ReviewFactory(product=self.product, user=self.user)
        resp = self.client.get(
            f"/reviews/{review.pk}/edit/",
            headers={"HX-Request": "true"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Edit your review", resp.content.decode())

    def test_cannot_edit_others_review(self):
        review = ReviewFactory(product=self.product, user=self.other_user)
        resp = self.client.post(
            f"/reviews/{review.pk}/edit/",
            {"rating": 1, "title": "Hacked", "body": "No"},
        )
        self.assertEqual(resp.status_code, 403)


class ReviewDeleteTest(TestCase):
    def setUp(self):
        self.user = UserFactory(password="testpass")
        self.other_user = UserFactory(password="testpass")
        self.product = ProductFactory()
        self.client.login(username=self.user.username, password="testpass")

    def test_delete_own_review(self):
        review = ReviewFactory(product=self.product, user=self.user)
        resp = self.client.post(f"/reviews/{review.pk}/delete/")
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Review.objects.filter(pk=review.pk).exists())

    def test_delete_htmx(self):
        review = ReviewFactory(product=self.product, user=self.user)
        resp = self.client.post(
            f"/reviews/{review.pk}/delete/",
            headers={"HX-Request": "true"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Review.objects.filter(pk=review.pk).exists())

    def test_cannot_delete_others_review(self):
        review = ReviewFactory(product=self.product, user=self.other_user)
        resp = self.client.post(f"/reviews/{review.pk}/delete/")
        self.assertEqual(resp.status_code, 403)
        self.assertTrue(Review.objects.filter(pk=review.pk).exists())

    def test_delete_requires_login(self):
        review = ReviewFactory(product=self.product)
        self.client.logout()
        resp = self.client.post(f"/reviews/{review.pk}/delete/")
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Review.objects.filter(pk=review.pk).exists())
