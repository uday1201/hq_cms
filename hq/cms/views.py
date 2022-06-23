from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *

from rest_framework.permissions import IsAuthenticated, IsAdminUser
# Create your views here.

class AssessmentViewSet(viewsets.ModelViewSet):
    queryset = Assessment.objects.all().order_by('-last_updated')
    serializer_class = AssessmentSerializer
    #permission_classes = (IsAuthenticated,IsAdminUser)

    def list(self, request):
        queryset = Assessment.objects.all().order_by('-last_updated')
        serializer = AssessmentSerializer(queryset, many=True)
        return Response(serializer.data)

"""
class AssessmentViews(APIView):
    def post(self, request):
        serializer = AssessmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status" : "Successful entry!", "data": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "error", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
"""

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all().order_by('-last_edited')
    serializer_class = QuestionSerializer
    #permission_classes = (IsAuthenticated,IsAdminUser)

class ExhibitViewSet(viewsets.ModelViewSet):
    queryset = Exhibit.objects.all().order_by('-created_on')
    serializer_class = ExhibitSerializer
    #permission_classes = (IsAuthenticated,IsAdminUser)

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all().order_by('-role_id')
    serializer_class = RoleSerializer
    #permission_classes = (IsAuthenticated,IsAdminUser)

class ExcelViewSet(viewsets.ModelViewSet):
    queryset = Excel.objects.all().order_by('-created_on')
    serializer_class = ExcelSerializer
    #permission_classes = (IsAuthenticated,IsAdminUser)

class CwfViewSet(viewsets.ModelViewSet):
    queryset = Cwf.objects.all().order_by('-cwf_id')
    serializer_class = CwfSerializer
    #permission_classes = (IsAuthenticated,IsAdminUser)

class KtViewSet(viewsets.ModelViewSet):
    queryset = Kt.objects.all().order_by('-kt_id')
    serializer_class = KtSerializer
    #permission_classes = (IsAuthenticated,IsAdminUser)

class StageViewSet(viewsets.ModelViewSet):
    queryset = Stage.objects.all().order_by('-stage_id')
    serializer_class = StageSerializer
    #permission_classes = (IsAuthenticated,IsAdminUser)

class QtypeViewSet(viewsets.ModelViewSet):
    queryset = Qtype.objects.all().order_by('-qtype_id')
    serializer_class = Qtype
    #permission_classes = (IsAuthenticated,IsAdminUser)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-last_updated_on')
    serializer_class = Comment
    #permission_classes = (IsAuthenticated,IsAdminUser)
