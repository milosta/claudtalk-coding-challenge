from django.urls import path, re_path

from .views import ProductDetailView, ProductListView

app_name = "catalog"

urlpatterns = [
    path("", ProductListView.as_view(), name="product-list"),
    re_path(r"^(?P<slug>[-a-zA-Z0-9_.]+)/$", ProductDetailView.as_view(), name="product-detail"),
]
