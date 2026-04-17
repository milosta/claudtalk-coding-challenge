import factory

from apps.catalog.models import Category, Product


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Category {n}")
    slug = factory.LazyAttribute(lambda o: o.name.lower().replace(" ", "-"))


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Sequence(lambda n: f"Product {n}")
    slug = factory.LazyAttribute(lambda o: o.name.lower().replace(" ", "-"))
    description = factory.Faker("paragraph", nb_sentences=3)
    category = factory.SubFactory(CategoryFactory)
