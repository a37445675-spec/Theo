from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BlogCategoryViewSet,
    BlogTagViewSet,
    CommentCreateViewSet,
    PostViewSet,
)

router = DefaultRouter()
router.register("posts", PostViewSet, basename="post")
router.register("categories", BlogCategoryViewSet, basename="blog-category")
router.register("tags", BlogTagViewSet, basename="blog-tag")
router.register("comments", CommentCreateViewSet, basename="comment")

app_name = "blog"

urlpatterns = [path("", include(router.urls))]
