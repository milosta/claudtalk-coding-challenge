from django.contrib.auth.decorators import login_required
from django.core.paginator import Page, Paginator
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from apps.catalog.models import Product

from .forms import ReviewForm
from .models import Review
from .services import get_product_aggregate

REVIEWS_PER_PAGE = 5


def _paginate_reviews(request: HttpRequest, product: Product) -> Page:
    paginator = Paginator(product.reviews.select_related("user"), REVIEWS_PER_PAGE)
    return paginator.get_page(request.GET.get("page"))


def _render_section(
    request: HttpRequest, product: Product, form: ReviewForm, status: int = 200
) -> HttpResponse:
    page = _paginate_reviews(request, product)
    context = {
        "product": product,
        "review_form": form,
        "reviews": page,
        "page_obj": page,
        "aggregate": get_product_aggregate(product.pk),
    }
    template = (
        "reviews/partials/_review_section.html" if request.htmx else "catalog/product_detail.html"
    )
    return render(request, template, context, status=status)


def _render_card_with_summary(request: HttpRequest, review: Review) -> HttpResponse:
    aggregate = get_product_aggregate(review.product_id)
    card = render_to_string(
        "reviews/partials/_review_card.html",
        {"review": review, "user": request.user},
        request=request,
    )
    summary = render_to_string(
        "reviews/partials/_rating_summary.html",
        {"aggregate": aggregate, "oob": True},
        request=request,
    )
    return HttpResponse(card + summary)


def review_card(request: HttpRequest, pk: int) -> HttpResponse:
    review = get_object_or_404(Review.objects.select_related("user"), pk=pk)
    return render(request, "reviews/partials/_review_card.html", {"review": review})


@login_required
@require_POST
def review_create(request: HttpRequest, slug: str) -> HttpResponse:
    product = get_object_or_404(Product, slug=slug)
    form = ReviewForm(request.POST, instance=Review(product=product, user=request.user))
    if form.is_valid():
        form.save()
        if request.htmx:
            return _render_section(request, product, ReviewForm())
        return redirect(product)
    return _render_section(request, product, form, status=400)


@login_required
def review_edit(request: HttpRequest, pk: int) -> HttpResponse:
    review = get_object_or_404(Review.objects.select_related("product", "user"), pk=pk)
    if review.user_id != request.user.id:
        return HttpResponseForbidden()

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            if request.htmx:
                review.refresh_from_db()
                return _render_card_with_summary(request, review)
            return redirect(review.product)
        if request.htmx:
            return render(
                request,
                "reviews/partials/_review_card_edit.html",
                {"review": review, "form": form},
                status=400,
            )
        return render(request, "reviews/edit.html", {"review": review, "form": form})

    form = ReviewForm(instance=review)
    if request.htmx:
        return render(
            request,
            "reviews/partials/_review_card_edit.html",
            {"review": review, "form": form},
        )
    return render(request, "reviews/edit.html", {"review": review, "form": form})


@login_required
@require_POST
def review_delete(request: HttpRequest, pk: int) -> HttpResponse:
    review = get_object_or_404(Review.objects.select_related("product"), pk=pk)
    if review.user_id != request.user.id:
        return HttpResponseForbidden()
    product = review.product
    review.delete()
    if request.htmx:
        return _render_section(request, product, ReviewForm())
    return redirect(product)


def review_list_page(request: HttpRequest, slug: str) -> HttpResponse:
    product = get_object_or_404(Product, slug=slug)
    page = _paginate_reviews(request, product)
    return render(
        request,
        "reviews/partials/_review_page.html",
        {"product": product, "reviews": page, "page_obj": page},
    )
