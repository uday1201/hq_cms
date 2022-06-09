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
    permission_classes = (IsAuthenticated,IsAdminUser)

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
    permission_classes = (IsAuthenticated,IsAdminUser)
