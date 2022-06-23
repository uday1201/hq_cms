from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *
from rest_framework.authtoken.models import Token
from django.core.exceptions import PermissionDenied


from rest_framework.permissions import IsAuthenticated, IsAdminUser
# Create your views here.

# authentication rule
def authenticate_token(self, request):
    access_token = request.headers['Authorization'].split(" ")[-1]
    #print(access_token)
    user=Token.objects.get(key=access_token).user
    #print('role: ', user.access_role )
    return {"user_id": user.id, "name": user.first_name ,"username": user.username, "role" :user.access_role}

def HasAdminAccess(user):
    return user['role'] == 'Admin'

class AssessmentViewSet(viewsets.ModelViewSet):
    queryset = Assessment.objects.all().order_by('-last_updated')
    serializer_class = AssessmentSerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        user = authenticate_token(self, request)
        if HasAdminAccess(user):
            queryset = Assessment.objects.all().order_by('-last_updated')
            serializer = AssessmentSerializer(queryset, many=True)
            return Response(serializer.data)
        else:
            raise PermissionDenied()


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
    permission_classes = (IsAuthenticated,)

class ExhibitViewSet(viewsets.ModelViewSet):
    queryset = Exhibit.objects.all().order_by('-created_on')
    serializer_class = ExhibitSerializer
    permission_classes = (IsAuthenticated,)

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all().order_by('-role_id')
    serializer_class = RoleSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']

class ExcelViewSet(viewsets.ModelViewSet):
    queryset = Excel.objects.all().order_by('-created_on')
    serializer_class = ExcelSerializer
    permission_classes = (IsAuthenticated,)

class CwfViewSet(viewsets.ModelViewSet):
    queryset = Cwf.objects.all().order_by('-cwf_id')
    serializer_class = CwfSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']

class KtViewSet(viewsets.ModelViewSet):
    queryset = Kt.objects.all().order_by('-kt_id')
    serializer_class = KtSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']

class StageViewSet(viewsets.ModelViewSet):
    queryset = Stage.objects.all().order_by('-stage_id')
    serializer_class = StageSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']

class QtypeViewSet(viewsets.ModelViewSet):
    queryset = Qtype.objects.all().order_by('-qtype_id')
    serializer_class = QtypeSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-last_updated_on')
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-first_name')
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get','put','patch']
