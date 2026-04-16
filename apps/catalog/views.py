from django.views.generic import DetailView, ListView

from .forms import ProductFilterForm
from .models import Product
from .search import build_search


class ProductListView(ListView):
    model = Product
    template_name = "catalog/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_template_names(self) -> list[str]:
        if getattr(self.request, "htmx", False):
            return ["catalog/partials/_product_grid.html"]
        return [self.template_name]

    def get_form(self) -> ProductFilterForm:
        return ProductFilterForm(self.request.GET or None)

    def get_queryset(self):
        qs = Product.objects.select_related("category")
        form = self.get_form()
        if not form.is_valid():
            return qs.order_by("-created_at")

        q = form.cleaned_data.get("q")
        category = form.cleaned_data.get("category")
        sort = form.cleaned_data.get("sort") or "newest"

        if category:
            qs = qs.filter(category=category)
        if q:
            qs = build_search(qs, q)
        else:
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
