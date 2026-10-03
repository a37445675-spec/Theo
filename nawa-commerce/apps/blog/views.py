from rest_framework import mixins, permissions, viewsets

from .models import BlogCategory, Comment, Post, BlogTag
from .serializers import BlogCategorySerializer, CommentCreateSerializer, PostDetailSerializer, PostListSerializer, BlogTagSerializer


class BlogCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BlogCategory.objects.all()
    serializer_class = BlogCategorySerializer
    lookup_field = "slug"
    permission_classes = [permissions.AllowAny]


class PostViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    permission_classes = [permissions.AllowAny]
    search_fields = ["title", "excerpt", "content"]
    filterset_fields = ["category__slug"]

    def get_serializer_class(self):
        return PostDetailSerializer if self.action == "retrieve" else PostListSerializer

    def get_queryset(self):
        return Post.objects.filter(status=Post.STATUS_PUBLISHED).select_related("category")


class CommentCreateViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentCreateSerializer
    permission_classes = [permissions.AllowAny]

class BlogTagViewSet(viewsets.ReadOnlyModelViewSet):
    """Liste des tags du blog (public)."""
    queryset = BlogTag.objects.all()
    serializer_class = BlogTagSerializer
    lookup_field = "slug"
    permission_classes = [permissions.AllowAny]
    pagination_class = None
