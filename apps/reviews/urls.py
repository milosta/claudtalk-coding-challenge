from django.urls import path

from . import views

app_name = "reviews"

urlpatterns = [
    path(
        "products/<slug:slug>/reviews/",
        views.review_create,
        name="create",
    ),
    path("reviews/<int:pk>/edit/", views.review_edit, name="edit"),
    path("reviews/<int:pk>/delete/", views.review_delete, name="delete"),
]
