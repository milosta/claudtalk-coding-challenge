from django.views.generic import DetailView, ListView

from .forms import ProductFilterForm
from .models import Product


class ProductListView(ListView):
    model = Product
    template_name = "catalog/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_form(self) -> ProductFilterForm:
        return ProductFilterForm(self.request.GET or None)

    def get_queryset(self):
        qs = Product.objects.select_related("category")
        form = self.get_form()
        if form.is_valid():
            q = form.cleaned_data.get("q")
            category = form.cleaned_data.get("category")
            sort = form.cleaned_data.get("sort") or "newest"
            if q:
                qs = qs.filter(name__icontains=q)
            if category:
                qs = qs.filter(category=category)
            qs = qs.order_by("name" if sort == "name" else "-created_at")
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["filter_form"] = self.get_form()
        return ctx


class ProductDetailView(DetailView):
    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"
    slug_url_kwarg = "slug"
