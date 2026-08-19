from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from apps.projects.models import Project
from apps.reviews.models import Review, ReviewIssue

class DashboardAnalyticsAPIView(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        projects = Project.objects.filter(owner=request.user)
        total_projects = projects.count()
        total_reviews = Review.objects.filter(project__owner=request.user).count()
        
        avg_score = 0
        if total_reviews > 0:
            total_score = sum(r.overall_score for r in Review.objects.filter(project__owner=request.user))
            avg_score = round(total_score / total_reviews, 1)

        total_issues = ReviewIssue.objects.filter(review__project__owner=request.user).count()

        return Response({
            "total_projects": total_projects,
            "total_reviews": total_reviews,
            "average_quality_score": avg_score,
            "critical_issues": total_issues
        })

class ProjectAnalyticsAPIView(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id, owner=request.user)
        except Project.DoesNotExist:
            return Response({"error": "Not Found"}, status=404)
        
        reviews = project.reviews.all().order_by('created_at')
        scores = [r.overall_score for r in reviews]
        dates = [r.created_at.strftime('%Y-%m-%d') for r in reviews]
        
        return Response({
            "project": project.name,
            "trend_labels": dates,
            "trend_scores": scores
        })
