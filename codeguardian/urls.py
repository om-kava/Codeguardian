from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.dashboard.views import (
    index_view, dashboard_view, projects_view, project_detail_view,
    review_studio_view, review_report_view, compare_view,
    login_view, register_view
)
from apps.dashboard.api_views import DashboardAnalyticsAPIView, ProjectAnalyticsAPIView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Frontend UI Pages
    path('', index_view, name='home'),
    path('dashboard/', dashboard_view, name='dashboard_page'),
    path('projects/', projects_view, name='projects_page'),
    path('projects/<int:project_id>/', project_detail_view, name='project_detail_page'),
    path('reviews/studio/', review_studio_view, name='review_studio_page'),
    path('reviews/<int:review_id>/report/', review_report_view, name='review_report_page'),
    path('reviews/compare/', compare_view, name='compare_page'),
    path('login/', login_view, name='login_page'),
    path('register/', register_view, name='register_page'),

    # REST API Routes
    path('api/auth/', include('apps.accounts.urls')),
    path('api/projects/', include('apps.projects.urls')),
    path('api/reviews/', include('apps.reviews.urls')),
    
    path('api/dashboard/', DashboardAnalyticsAPIView.as_view(), name='api_dashboard_analytics'),
    path('api/projects/<int:project_id>/analytics/', ProjectAnalyticsAPIView.as_view(), name='api_project_analytics'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
