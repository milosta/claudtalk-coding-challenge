import random

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.tests.factories import UserFactory
from apps.catalog.tests.factories import CategoryFactory, ProductFactory
from apps.reviews.tests.factories import ReviewFactory

CATEGORIES = [
    "Headphones",
    "Speakers",
    "Microphones",
    "Webcams",
    "Phone Systems",
]

PRODUCT_NAMES = {
    "Headphones": [
        "CloudTalk Pro Wireless",
        "CloudTalk Studio Monitor",
        "CloudTalk Sport Earbuds",
        "CloudTalk Noise Cancelling 700",
        "CloudTalk Kids Safe",
    ],
    "Speakers": [
        "CloudTalk SoundBar 2.1",
        "CloudTalk Portable Mini",
        "CloudTalk Conference Puck",
        "CloudTalk Desktop Duo",
        "CloudTalk Outdoor Blast",
    ],
    "Microphones": [
        "CloudTalk USB Condenser",
        "CloudTalk Lavalier Pro",
        "CloudTalk Shotgun Boom",
        "CloudTalk Podcast Kit",
        "CloudTalk Dynamic SM-7",
    ],
    "Webcams": [
        "CloudTalk 4K Ultra HD",
        "CloudTalk Streaming Pro",
        "CloudTalk Wide Angle 120",
        "CloudTalk Mini Clip",
        "CloudTalk Auto-Track AI",
    ],
    "Phone Systems": [
        "CloudTalk VoIP Desk Phone",
        "CloudTalk Cordless DECT",
        "CloudTalk Conference Bridge",
        "CloudTalk Receptionist Console",
        "CloudTalk Softphone Headset",
    ],
}

DESCRIPTIONS = [
    "Crystal-clear audio quality with advanced noise reduction. "
    "Perfect for daily calls and music listening. "
    "Built with premium materials for lasting comfort.",
    "Professional-grade sound reproduction for the most demanding users. "
    "Features an ergonomic design that keeps you comfortable all day. "
    "Backed by our two-year warranty.",
    "Compact and lightweight without compromising on performance. "
    "Quick setup — just plug in and start using it. "
    "Compatible with all major platforms and devices.",
    "Next-generation technology meets elegant design. "
    "Smart features adapt to your environment automatically. "
    "Recommended by industry professionals worldwide.",
    "Versatile and reliable for both home and office use. "
    "Intuitive controls make it easy for anyone to operate. "
    "Exceptional value for the quality delivered.",
]

REVIEW_TITLES = [
    "Absolutely love it!",
    "Great value for money",
    "Exceeded my expectations",
    "Solid product, minor issues",
    "Does the job well",
    "Not what I expected",
    "Perfect for my needs",
    "Good but could be better",
    "Outstanding quality",
    "Would buy again",
    "Decent for the price",
    "Best purchase this year",
]

REVIEW_BODIES = [
    "I've been using this for a few weeks now and I'm very impressed. "
    "The build quality is excellent and it performs exactly as advertised.",
    "Setup was a breeze and it started working right out of the box. "
    "Sound quality is remarkable for this price range.",
    "After comparing several options, I went with this one and don't regret it. "
    "It's become an essential part of my daily workflow.",
    "Works well for the most part. I had a minor issue with connectivity "
    "at first, but after a firmware update everything has been smooth.",
    "I use this for hours every day and it's held up perfectly. "
    "Very comfortable and the audio quality is top-notch.",
    "Good product overall. The only downside is the packaging was a bit "
    "excessive, but the product itself is well made.",
    "This replaced my old unit and the improvement is night and day. "
    "Highly recommend for anyone looking to upgrade.",
    "Bought this for my home office and it's been a game changer. "
    "Crystal clear calls and easy to set up with my existing equipment.",
]


class Command(BaseCommand):
    help = "Populate the database with demo data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing demo data before seeding",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        from apps.catalog.models import Category, Product
        from apps.reviews.models import Review
        from django.contrib.auth import get_user_model

        User = get_user_model()

        if options["flush"]:
            Review.objects.all().delete()
            Product.objects.all().delete()
            Category.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write("Flushed existing data.")

        rng = random.Random(42)

        categories = {}
        for name in CATEGORIES:
            categories[name] = CategoryFactory(name=name, slug=name.lower().replace(" ", "-"))
        self.stdout.write(f"Created {len(categories)} categories")

        products = []
        for cat_name, product_names in PRODUCT_NAMES.items():
            for pname in product_names:
                p = ProductFactory(
                    name=pname,
                    category=categories[cat_name],
                    description=rng.choice(DESCRIPTIONS),
                )
                products.append(p)
        self.stdout.write(f"Created {len(products)} products")

        users = [UserFactory() for _ in range(10)]
        self.stdout.write(f"Created {len(users)} users")

        review_count = 0
        for product in products:
            reviewers = rng.sample(users, k=rng.randint(2, 7))
            for user in reviewers:
                ReviewFactory(
                    product=product,
                    user=user,
                    rating=rng.randint(1, 5),
                    title=rng.choice(REVIEW_TITLES),
                    body=rng.choice(REVIEW_BODIES),
                )
                review_count += 1
        self.stdout.write(f"Created {review_count} reviews")

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully!"))
