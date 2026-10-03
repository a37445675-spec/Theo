"""URLs pour les formulaires."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FormDefinitionViewSet, FormSubmissionViewSet

router = DefaultRouter()
router.register(r"definitions", FormDefinitionViewSet, basename="form-definition")
router.register(r"submissions", FormSubmissionViewSet, basename="form-submission")

urlpatterns = [
    path("", include(router.urls)),
]
