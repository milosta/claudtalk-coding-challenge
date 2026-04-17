from django.urls import path

from . import views

app_name = "reviews"

urlpatterns = [
    path(
        "products/<slug:slug>/reviews/",
        views.review_create,
        name="create",
    ),
    path(
        "products/<slug:slug>/reviews/page/",
        views.review_list_page,
        name="page",
    ),
    path("reviews/<int:pk>/", views.review_card, name="card"),
    path("reviews/<int:pk>/edit/", views.review_edit, name="edit"),
    path("reviews/<int:pk>/delete/", views.review_delete, name="delete"),
]
