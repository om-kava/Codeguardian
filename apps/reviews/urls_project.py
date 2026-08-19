from django.urls import path
from .views import ProjectReviewListView

urlpatterns = [
    path('', ProjectReviewListView.as_view(), name='api_project_reviews_list'),
]
