from django.urls import path

from .views import ProductDetailView, ProductListView

app_name = "catalog"

urlpatterns = [
    path("", ProductListView.as_view(), name="product-list"),
    path("<slug:slug>/", ProductDetailView.as_view(), name="product-detail"),
]
