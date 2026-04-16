from django import forms
from django.core.exceptions import ValidationError

from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "title", "body"]
        widgets = {
            "rating": forms.Select(
                choices=[(i, f"{i} / 5") for i in range(5, 0, -1)],
                attrs={"class": "w-full px-3 py-2 border border-slate-300 rounded"},
            ),
            "title": forms.TextInput(
                attrs={
                    "placeholder": "Summary",
                    "maxlength": 120,
                    "class": "w-full px-3 py-2 border border-slate-300 rounded",
                },
            ),
            "body": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Your review",
                    "class": "w-full px-3 py-2 border border-slate-300 rounded",
                },
            ),
        }

    def clean(self) -> dict:
        cleaned = super().clean()
        product_id = getattr(self.instance, "product_id", None)
        user_id = getattr(self.instance, "user_id", None)
        if product_id and user_id:
            qs = Review.objects.filter(product_id=product_id, user_id=user_id)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("You've already reviewed this product.")
        return cleaned
