import factory

from apps.accounts.tests.factories import UserFactory
from apps.catalog.tests.factories import ProductFactory
from apps.reviews.models import Review


class ReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Review

    product = factory.SubFactory(ProductFactory)
    user = factory.SubFactory(UserFactory)
    rating = factory.Faker("random_int", min=1, max=5)
    title = factory.Faker("sentence", nb_words=4)
    body = factory.Faker("paragraph", nb_sentences=2)
