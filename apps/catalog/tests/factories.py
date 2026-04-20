import factory
from django.utils.text import slugify

from apps.catalog.models import Category, Product


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Category {n}")
    slug = factory.LazyAttribute(lambda o: slugify(o.name))


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Sequence(lambda n: f"Product {n}")
    slug = factory.LazyAttribute(lambda o: slugify(o.name))
    description = factory.Faker("paragraph", nb_sentences=3)
    category = factory.SubFactory(CategoryFactory)
