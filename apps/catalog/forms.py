from django import forms

from .models import Category

SORT_CHOICES = [
    ("newest", "Newest"),
    ("name", "Name (A–Z)"),
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
    sort = forms.ChoiceField(
        required=False,
        choices=SORT_CHOICES,
        initial="newest",
    )
