from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "title", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("title", "body", "product__name", "user__username")
    autocomplete_fields = ("product", "user")
    date_hierarchy = "created_at"
