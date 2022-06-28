from django.shortcuts import render
from requests import request

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
    access_token = request.COOKIES.get('auth_token')
    print(access_token)
    user=Token.objects.get(key=access_token).user
    print('role: ', user.access_role )
    return {"user_id": user.id, "name": user.first_name ,"username": user.username, "role" :user.access_role}

def HasAdminAccess(user):
    return user['role'] == 'Admin'


class AssessmentSetPagination(PageNumberPagination):
    page_size = 20
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

    def post(self, request):
        print("question")
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            return Response()
        
        print(serializer.errors)

    def list(self, request):
        queryset = Question.objects.all()
        #print(request.GET["assessmentid"])
        if "assessmentid" in request.GET:
            queryset = queryset.filter(assessments__id= request.GET["assessmentid"]).distinct()

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

    # def create(self, request):
    #     content = request.data
    #     # get assessment id from the question response
    #     if "assessmentid" in content:
    #         assessment_id = content["assessmentid"]
    #         # delete it from the content field
    #         assessment = Assessment.objects.filter(aid = assessment_id)
    #         for a in assessment:
    #             print(a.qlist)
    #         del content["assessmentid"]
    #     print(content)

class ExhibitViewSet(viewsets.ModelViewSet):
    queryset = Exhibit.objects.all().order_by('-created_on')
    serializer_class = ExhibitSerializer
    permission_classes = (IsAuthenticated,)

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all().order_by('-id')
    serializer_class = RoleSerializer

    def get_permissions(self):
        """
        Custom permissions, allow members to read only
        """
        user = authenticate_token(self, self.request)
        #print(user["role"])
        if user["role"] == 'ADMIN':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [ReadOnly]
        return [permission() for permission in permission_classes]

class ExcelViewSet(viewsets.ModelViewSet):
    queryset = Excel.objects.all().order_by('-created_on')
    serializer_class = ExcelSerializer
    permission_classes = (IsAuthenticated,)

class CwfViewSet(viewsets.ModelViewSet):
    queryset = Cwf.objects.all().order_by('-id')
    serializer_class = CwfSerializer

    def get_permissions(self):
        """
        Custom permissions, allow members to read only
        """
        user = authenticate_token(self, self.request)
        #print(user["role"])
        if user["role"] == 'ADMIN':
            permission_classes = [AllowAny]
        else:
            permission_classes = [ReadOnly]
        return [permission() for permission in permission_classes]

class KtViewSet(viewsets.ModelViewSet):
    queryset = Kt.objects.all().order_by('-id')
    serializer_class = KtSerializer

    def get_permissions(self):
        """
        Custom permissions, allow members to read only
        """
        user = authenticate_token(self, self.request)
        #print(user["role"])
        if user["role"] == 'ADMIN':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [ReadOnly]
        return [permission() for permission in permission_classes]

class StageViewSet(viewsets.ModelViewSet):
    queryset = Stage.objects.all().order_by('-id')
    serializer_class = StageSerializer

    def get_permissions(self):
        """
        Custom permissions, allow members to read only
        """
        user = authenticate_token(self, self.request)
        #print(user["role"])
        if user["role"] == 'ADMIN':
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
    permission_classes = (AllowAny,)
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
        response = {}
        #roleid = request.GET["role_code"]
        if "role_code" in request.GET:
            roleid = [request.GET["role_code"]]
        else:
            roleid = Role.objects.all().values_list('id', flat=True)
        print(roleid)
        for role in roleid:
            label = Role.objects.filter(id=role).values('name')
            cwfs = Cwf.objects.filter(role__id=role).distinct()
            cwf_main ={}
            for cwf in cwfs:
                cwf_obj = {}
                cwflabel = cwf.name
                cwfcode = cwf.id
                kts = Kt.objects.filter(cwf__id = cwf.id).distinct()
                #print(kts)
                kt_array =[]
                for kt in kts:
                    if kt.name is not None:
                        ktname = kt.name
                        ktcode = kt.id
                        kt_array.append({"label":ktname, "value":ktcode})
                cwf_obj["keyTasks"] = kt_array
                cwf_obj["label"] = cwflabel
                cwf_main[cwfcode] = cwf_obj
            stages = Stage.objects.filter(role__id=role).distinct()
            stage_array =[]
            for stage in stages:
                #print(stage.code)
                if stage.name is not None:
                    stage_array.append({stage.id:stage.name})
            response[role]={"label":label[0]["name"],"wf":cwf_main, "stages":stage_array}
        return Response(response)



class SnippetViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
