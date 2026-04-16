from django import forms

from .models import Category

SORT_CHOICES = [
    ("newest", "Newest"),
    ("rating", "Top rated"),
    ("name", "Name (A–Z)"),
]

MIN_RATING_CHOICES = [
    ("", "Any rating"),
    ("5", "5 stars"),
    ("4", "4+ stars"),
    ("3", "3+ stars"),
    ("2", "2+ stars"),
    ("1", "1+ stars"),
]


class ProductFilterForm(forms.Form):
    q = forms.CharField(
        required=False,
        label="Search",
        widget=forms.TextInput(attrs={"placeholder": "Search products…"}),
    )
    category = forms.ModelChoiceField(
        required=False,
        queryset=Category.objects.all(),
        empty_label="All categories",
    )
    min_rating = forms.ChoiceField(
        required=False,
        choices=MIN_RATING_CHOICES,
    )
    sort = forms.ChoiceField(
        required=False,
        choices=SORT_CHOICES,
        initial="newest",
    )
