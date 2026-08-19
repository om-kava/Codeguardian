from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, SubmissionCreateView

router = DefaultRouter()
router.register(r'', ProjectViewSet, basename='project')

urlpatterns = [
    path('<int:project_id>/submissions/', SubmissionCreateView.as_view(), name='api_create_submission'),
    path('<int:project_id>/reviews/', include('apps.reviews.urls_project')), # Create this helper
    path('', include(router.urls)),
]
