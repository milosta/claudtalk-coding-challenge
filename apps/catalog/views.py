from django.db.models import Avg, Count, F
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
        qs = Product.objects.select_related("category").annotate(
            avg_rating=Avg("reviews__rating"),
            review_count=Count("reviews"),
        )
        form = self.get_form()
        if not form.is_valid():
            return qs.order_by("-created_at")

        q = form.cleaned_data.get("q")
        category = form.cleaned_data.get("category")
        min_rating = form.cleaned_data.get("min_rating")
        sort = form.cleaned_data.get("sort") or "newest"

        if category:
            qs = qs.filter(category=category)
        if min_rating:
            qs = qs.filter(avg_rating__gte=int(min_rating))
        if q:
            qs = build_search(qs, q)
        elif sort == "rating":
            qs = qs.order_by(F("avg_rating").desc(nulls_last=True), "-created_at")
        elif sort == "name":
            qs = qs.order_by("name")
        else:
            qs = qs.order_by("-created_at")
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

    def get_context_data(self, **kwargs):
        from apps.reviews.forms import ReviewForm
        from apps.reviews.services import get_product_aggregate
        from apps.reviews.views import REVIEWS_PER_PAGE

        from django.core.paginator import Paginator

        ctx = super().get_context_data(**kwargs)
        paginator = Paginator(self.object.reviews.select_related("user"), REVIEWS_PER_PAGE)
        page = paginator.get_page(self.request.GET.get("page"))
        ctx["review_form"] = ReviewForm()
        ctx["reviews"] = page
        ctx["page_obj"] = page
        ctx["aggregate"] = get_product_aggregate(self.object.pk)
        return ctx
