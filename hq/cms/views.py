from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *
from rest_framework.authtoken.models import Token
from django.core.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination

from rest_framework.permissions import IsAuthenticated, IsAdminUser, BasePermission, SAFE_METHODS, AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from django.views.decorators.csrf import csrf_exempt


# token authentication custom oveeride
class CustomObtainAuthToken(ObtainAuthToken):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        response = super(CustomObtainAuthToken, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        user = token.user
        return Response({'token': token.key, 'id': user.id, 'role': user.access_role, "name": user.first_name + ' ' + user.last_name})

# Create your views here.

class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

# authentication rule
def authenticate_token(self, request):
    access_token = request.headers['Authorization'].split(" ")[-1]
    #print(access_token)
    user=Token.objects.get(key=access_token).user
    #print('role: ', user.access_role )
    return {"user_id": user.id, "name": user.first_name ,"username": user.username, "role" :user.access_role}

def HasAdminAccess(user):
    return user['role'] == 'Admin'


class AssessmentSetPagination(PageNumberPagination):
    page_size = 1
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    max_page_size = 1000

class AssessmentViewSet(viewsets.ModelViewSet):
    queryset = Assessment.objects.all().order_by('-last_updated')
    serializer_class = AssessmentSerializer
    pagination_class = AssessmentSetPagination
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = authenticate_token(self, request)
        #print(user["user_id"])
        # Admin can view everything
        if user["role"] == "MEMBER":
            queryset = Assessment.objects.filter(creator=user["user_id"]) | Assessment.objects.filter(assigned_to=user["user_id"])
        else:
            queryset = Assessment.objects.all()

        print(request.GET)
        if "status" in request.GET:
            queryset = queryset.filter(status=request.GET["status"]).distinct()

        if "created_by" in request.GET:
            queryset = queryset.filter(creator = request.headers["created_by"]).distinct()

        if "role" in request.GET:
            queryset = queryset.filter(role=request.GET["role"]).distinct()

        if "starttime" in request.GET and "endtime" in request.GET:
            queryset = queryset.filter(created__range=[request.GET["starttime"],request.GET["endtime"]]).distinct()

        queryset_order = queryset.order_by('-last_updated')
        serializer = AssessmentSerializer(queryset_order, many=True)
        page = self.paginate_queryset(serializer.data)
        return Response(page)


class Logout(APIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post']
    def post(self, request):
        return self.logout(request)

    def logout(self, request):
        try:
            request.user.auth_token.delete()
        except (AttributeError):
            pass
        return Response({"success": "Successfully logged out."},
                        status=status.HTTP_200_OK)

class QuestionSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    pagination_class = AssessmentSetPagination
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        queryset = Question.objects.all()
        #print(request.GET["assessmentid"])
        if "assessmentid" in request.GET:
            queryset = queryset.filter(assessments__aid= request.GET["assessmentid"]).distinct()

        if "cwf" in request.GET:
            queryset = queryset.filter(cwf=request.GET["cwf"]).distinct()

        if "kt" in request.GET:
            queryset = queryset.filter(kt=request.GET["kt"]).distinct()

        if "created_by" in request.GET:
            queryset = queryset.filter(creator = request.GET["created_by"]).distinct()

        if "role" in request.GET:
            queryset = queryset.filter(role=request.GET["role"]).distinct()

        if "starttime" in request.GET and "endtime" in request.GET:
            queryset = queryset.filter(created__range=[request.GET["starttime"],request.GET["endtime"]]).distinct()

        queryset_order = queryset.order_by('-last_edited')
        serializer = QuestionSerializer(queryset, many=True)
        page = self.paginate_queryset(serializer.data)
        return Response(page)

class ExhibitViewSet(viewsets.ModelViewSet):
    queryset = Exhibit.objects.all().order_by('-created_on')
    serializer_class = ExhibitSerializer
    permission_classes = (IsAuthenticated,)

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all().order_by('-role_id')
    serializer_class = RoleSerializer

    def get_permissions(self):
        """
        Custom permissions, allow members to read only
        """
        access_token = self.request.headers['Authorization'].split(" ")[-1]
        user=Token.objects.get(key=access_token).user
        print(user.access_role)
        if user.access_role == 'ADMIN':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [ReadOnly]
        return [permission() for permission in permission_classes]

class ExcelViewSet(viewsets.ModelViewSet):
    queryset = Excel.objects.all().order_by('-created_on')
    serializer_class = ExcelSerializer
    permission_classes = (IsAuthenticated,)

class CwfViewSet(viewsets.ModelViewSet):
    queryset = Cwf.objects.all().order_by('-cwf_id')
    serializer_class = CwfSerializer

    def get_permissions(self):
        """
        Custom permissions, allow members to read only
        """
        access_token = self.request.headers['Authorization'].split(" ")[-1]
        user=Token.objects.get(key=access_token).user
        print(user.access_role)
        if user.access_role == 'ADMIN':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [ReadOnly]
        return [permission() for permission in permission_classes]

class KtViewSet(viewsets.ModelViewSet):
    queryset = Kt.objects.all().order_by('-kt_id')
    serializer_class = KtSerializer


    def get_permissions(self):
        """
        Custom permissions, allow members to read only
        """
        access_token = self.request.headers['Authorization'].split(" ")[-1]
        user=Token.objects.get(key=access_token).user
        print(user.access_role)
        if user.access_role == 'ADMIN':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [ReadOnly]
        return [permission() for permission in permission_classes]

class StageViewSet(viewsets.ModelViewSet):
    queryset = Stage.objects.all().order_by('-stage_id')
    serializer_class = StageSerializer


    def get_permissions(self):
        """
        Custom permissions, allow members to read only
        """
        access_token = self.request.headers['Authorization'].split(" ")[-1]
        user=Token.objects.get(key=access_token).user
        print(user.access_role)
        if user.access_role == 'ADMIN':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [ReadOnly]
        return [permission() for permission in permission_classes]

class QtypeViewSet(viewsets.ModelViewSet):
    queryset = Qtype.objects.all().order_by('-qtype_id')
    serializer_class = QtypeSerializer

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-last_updated_on')
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-first_name')
    serializer_class = UserSerializer
    permission_classes = (AllowAny)
    # def get_permissions(self):
    #     """
    #     Custom permissions, allow members to read only
    #     """
    #     access_token = self.request.headers['Authorization'].split(" ")[-1]
    #     user=Token.objects.get(key=access_token).user
    #     print(user.access_role)
    #     if user.access_role == 'ADMIN':
    #         permission_classes = [IsAuthenticated]
    #     else:
    #         permission_classes = [ReadOnly]
    #     return [permission() for permission in permission_classes]

class CwfKtStage(APIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']

    def get(self, request, format=None):
        response =[]
        roleid = request.GET["roleid"][0]
        label = Role.objects.filter(role_id=roleid).values('role_name')[0]['role_name']
        cwfs = Cwf.objects.filter(role__role_id=roleid).distinct()
        cwf_array =[]
        for cwf in cwfs:
            cwflabel = cwf.name
            cwfcode = cwf.code
            kts = Kt.objects.filter(cwf__cwf_id = cwf.cwf_id).distinct()
            #print(kts)
            kt_array =[]
            for kt in kts:
                if kt.name is not None:
                    ktname = kt.name
                    ktcode = kt.code
                    kt_array.append({"Key Task Code":ktcode, "Key Task Name":ktname})
            cwf_array.append({cwflabel:kt_array})
        stages = Stage.objects.filter(role__role_id=roleid).distinct()
        stage_array =[]
        for stage in stages:
            print(stage.code)
            if stage.name is not None:
                stage_array.append({stage.code:stage.name})
        response.append({"Role id":roleid,"CWF":cwf_array, "Stages":stage_array})
        return Response(response)



class SnippetViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
