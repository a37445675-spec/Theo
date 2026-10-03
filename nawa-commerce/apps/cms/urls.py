from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DynamicTagViewSet, PageTemplateViewSet, SiteKitApplyView, SiteKitViewSet

router = DefaultRouter()
router.register("templates", PageTemplateViewSet, basename="page-template")
router.register("dynamic-tags", DynamicTagViewSet, basename="dynamic-tag")
router.register("site-kits", SiteKitViewSet, basename="site-kit")

app_name = "cms"

urlpatterns = [
    path("site-kits/apply/<int:pk>/", SiteKitApplyView.as_view(), name="site-kit-apply"),
    path("", include(router.urls)),
]
