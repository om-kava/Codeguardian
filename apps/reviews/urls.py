from django.urls import path
from .views import (
    ProjectReviewListView, ReviewDetailView, FetchGitHubView,
    AnalyzeInstantView, SubmitReviewView, AuditRepositoryView, CompareReviewsView,
    ReviewListView
)

urlpatterns = [
    path('', ReviewListView.as_view(), name='api_review_list'),
    path('fetch_github/', FetchGitHubView.as_view(), name='api_fetch_github'),
    path('fetch-github/', FetchGitHubView.as_view(), name='api_fetch_github_alias'),
    path('analyze_instant/', AnalyzeInstantView.as_view(), name='api_analyze_instant'),
    path('analyze-instant/', AnalyzeInstantView.as_view(), name='api_analyze_instant_alias'),
    path('submit/', SubmitReviewView.as_view(), name='api_submit_review'),
    path('audit_repo/', AuditRepositoryView.as_view(), name='api_audit_repo'),
    path('audit-repo/', AuditRepositoryView.as_view(), name='api_audit_repo_alias'),
    path('compare/', CompareReviewsView.as_view(), name='api_compare_reviews'),
    
    path('<int:pk>/', ReviewDetailView.as_view(), name='api_review_detail'),
    path('project/<int:project_id>/', ProjectReviewListView.as_view(), name='api_project_reviews'),
]
