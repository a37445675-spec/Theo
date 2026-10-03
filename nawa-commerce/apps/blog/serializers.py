from rest_framework import serializers

from .models import BlogCategory, Comment, Post, BlogTag


class BlogTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogTag
        fields = ["id", "name", "slug"]


class BlogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = ["id", "name", "slug"]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "author_name", "content", "created_at"]


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["post", "author_name", "author_email", "content"]


class PostListSerializer(serializers.ModelSerializer):
    category = BlogCategorySerializer(read_only=True)

    class Meta:
        model = Post
        fields = ["id", "title", "slug", "excerpt", "category", "published_at"]


class PostDetailSerializer(serializers.ModelSerializer):
    category = BlogCategorySerializer(read_only=True)
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ["id", "title", "slug", "excerpt", "content", "category", "comments", "published_at", "meta_title", "meta_description"]

    def get_comments(self, obj):
        return CommentSerializer(obj.comments.filter(status=Comment.STATUS_APPROVED), many=True).data
