from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.catalog.models import Product

from .forms import ReviewForm
from .models import Review


def _render_section(
    request: HttpRequest, product: Product, form: ReviewForm, status: int = 200
) -> HttpResponse:
    context = {
        "product": product,
        "review_form": form,
        "reviews": product.reviews.select_related("user"),
    }
    template = (
        "reviews/partials/_review_section.html" if request.htmx else "catalog/product_detail.html"
    )
    return render(request, template, context, status=status)


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
    review = get_object_or_404(Review.objects.select_related("product"), pk=pk)
    if review.user_id != request.user.id:
        return HttpResponseForbidden()

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            if request.htmx:
                return _render_section(request, review.product, ReviewForm())
            return redirect(review.product)
    else:
        form = ReviewForm(instance=review)

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
