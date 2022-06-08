from django.shortcuts import render

from rest_framework import viewsets

from .serializers import *
from .models import *

# Create your views here.
class AssessmentViewSet(viewsets.ModelViewSet):
    queryset = Assessment.objects.all().order_by('-last_updated')
    serializer_class = AssessmentSerializer

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all().order_by('-last_edited')
    serializer_class = QuestionSerializer
    
