from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return

from .models import Project, CodeSubmission
from .serializers import ProjectSerializer, CodeSubmissionSerializer
from apps.reviews.models import Review, ReviewIssue
from apps.reviews.serializers import ReviewSerializer
from apps.analyzer.engine import run_analysis

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    authentication_classes = [JWTAuthentication, CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class SubmissionCreateView(generics.CreateAPIView):
    serializer_class = CodeSubmissionSerializer
    authentication_classes = [JWTAuthentication, CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id, owner=request.user)
        except Project.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        submission = serializer.save(project=project)
        
        # Trigger deterministic static analysis synchronously for MVP
        try:
            review = run_analysis(submission)
            return Response({
                "message": "Code submitted and analyzed successfully.",
                "submission_id": submission.id,
                "review_id": review.id
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            # Handle AI or analysis failure gracefully
            return Response({
                "message": "Submission stored, but analysis failed.",
                "error": str(e),
                "submission_id": submission.id
            }, status=status.HTTP_201_CREATED)
