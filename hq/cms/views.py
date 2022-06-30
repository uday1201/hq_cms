from django.shortcuts import render
from requests import request
import json
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
    #access_token = request.COOKIES.get('auth_token')
    access_token = request.headers['Authorization'].split(" ")[-1]
    #print(access_token)
    user=Token.objects.get(key=access_token).user
    print('role: ', user.access_role )
    return {"user_id": user.id, "name": user.first_name ,"username": user.username, "role" :user.access_role}


class AssessmentSetPagination(PageNumberPagination):
    page_size = 20
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    max_page_size = 1000

class AssessmentViewSet(viewsets.ModelViewSet):
    queryset = Assessment.objects.filter(isdeleted=False).order_by('-last_updated')
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
            queryset = Assessment.objects.filter(isdeleted=False)

        #print(request.GET)
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

# function to get comments of the questions queryset
def get_comments(queryset):
    for q in queryset:
        comments = []
        for comment in Comment.objects.filter(question = q).order_by('-last_updated_on'):
            print(comment)
            comments.append(
                {
                    "id" : comment.id,
                    "author" : comment.author.username,
                    "content" : comment.content,
                    "date_posted": comment.date_posted
                }
            )
        print(comments)
        q.comments = comments
    return queryset

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.filter(isdeleted=False)
    serializer_class = QuestionSerializer
    pagination_class = QuestionSetPagination
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        queryset = Question.objects.filter(isdeleted=False)
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

        # return comments linked to the questions
        queryset = get_comments(queryset)

        queryset_order = queryset.order_by('-last_edited')
        serializer = QuestionSerializer(queryset, many=True)
        page = self.paginate_queryset(serializer.data)
        return Response(page)

    def retrieve(self, request, pk=None):
        queryset = Question.objects.filter(isdeleted=False).filter(id=pk)
        # return comments linked to the question
        queryset = get_comments(queryset)
        serializer = QuestionSerializer(queryset, many=True)
        return Response(serializer.data[0])

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
    queryset = Exhibit.objects.filter(isdeleted=False).order_by('-created_on')
    serializer_class = ExhibitSerializer
    permission_classes = (IsAuthenticated,)

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.filter(isdeleted=False).order_by('-id')
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
    queryset = Excel.objects.filter(isdeleted=False).order_by('-created_on')
    serializer_class = ExcelSerializer
    permission_classes = (IsAuthenticated,)

class CwfViewSet(viewsets.ModelViewSet):
    queryset = Cwf.objects.filter(isdeleted=False).order_by('-id')
    serializer_class = CwfSerializer

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

class KtViewSet(viewsets.ModelViewSet):
    queryset = Kt.objects.filter(isdeleted=False).order_by('-id')
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
    queryset = Stage.objects.filter(isdeleted=False).order_by('-id')
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
    queryset = Comment.objects.filter(isdeleted=False).order_by('-last_updated_on')
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(isdeleted=False).order_by('-first_name')
    serializer_class = UserSerializer
    http_method_names = ['get','post','patch']

    def list(self, request):
        user = authenticate_token(self, request)
        queryset = User.objects.filter(id = user["user_id"])
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        user = authenticate_token(self, request)
        if int(pk) == int(user["user_id"]):
            return super().partial_update(request, pk)
        else:
            return Response({"Not Authorized": "You don't have access to this entry"},status=status.HTTP_401_UNAUTHORIZED)

    def retrieve(self, request, pk=None):
        user = authenticate_token(self, request)
        if pk == user["user_id"]:
            queryset = User.objects.filter(id = user["user_id"])
            serializer = UserSerializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({"Not Authorized": "You don't have access to this entry"},status=status.HTTP_401_UNAUTHORIZED)


class CwfKtStage(APIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get','post']

    def post(self, request):
        access_token = request.headers['Authorization'].split(" ")[-1]
        user=Token.objects.get(key=access_token).user
        reqs = request.body.decode('utf-8')
        valid_data = json.loads(reqs)
        print(valid_data["role"].get("label"))
        if not valid_data.get("role"):
            return status.HTTP_500_INTERNAL_SERVER_ERROR

        if not valid_data["role"].get("value"):
            #role = create_role()
            role = Role.objects.create(
                id = "dummyid11",
                name = valid_data["role"].get("label"),
                creator = user
            )
            print(user)
            role.save()
            role_id = role.id
        else:
            Role.objects.filter(
            id = valid_data["role"].get("value")
            ).update(
                name = valid_data["role"].get("label")
            )
            role_id = valid_data["role"].get("value")
        print(role_id)
        for i in range(len(valid_data.get("stage"))):
            cstage = valid_data["stage"][i]
            if not cstage.get("value"):
                stage = Stage.objects.create(
                    id = "dummyid11",
                    name = cstage.get("label"),
                    creator = user
                )
                stage.role.set([role_id])
                stage.save()
            else:
                stage = Stage.objects.get(
                    id = cstage.get("value")
                )
                stage.name = cstage.get("label")
                stage.role.add(role_id)
                stage.save()
            stage_id = stage.id

        for i in range(len(valid_data.get("wf"))):
            wfdata = valid_data["wf"][i]
            if not wfdata.get("value"):
                cwfun = Cwf.objects.create(
                    id = "dummyid11",
                    name = wfdata.get("label"),
                    creator = user
                )
                cwfun.role.set([role_id])
                cwfun.save()

            else:
                cwfun = Cwf.objects.get(
                    id = wfdata.get("value")
                )
                cwfun.name = wfdata.get("label")
                cwfun.role.add(role_id)
                cwfun.save()
            cwf_id = cwfun.id

            for j in range(len(wfdata["keyTask"])):
                ktdata = wfdata["keyTask"][j]
                if not ktdata.get("value"):
                    kt = Kt.objects.create(
                        id = "dummyid11",
                        name = ktdata.get("label"),
                        creator = user
                    )
                    kt.role.set([role_id])
                    kt.cwf.set([cwf_id])
                    kt.save()
                else:
                    kt = Kt.objects.get(
                        id = ktdata.get("value")
                    )
                    kt.name = ktdata.get("label")
                    kt.role.add(role_id)
                    kt.cwf.add(cwf_id)
                    kt.save()
        return Response({"success": "Successfully created"},
                        status=status.HTTP_200_OK)

    def get(self, request, format=None):
        response = {}
        role_obj = Role.objects.filter(isdeleted=False)
        if "role_code" in request.GET:
            roleid = [request.GET["role_code"]]
        else:
            roleid = role_obj.values_list('id', flat=True)
        print(roleid)
        for role in roleid:
            label = role_obj.filter(id=role).values('name')
            cwfs = Cwf.objects.filter(isdeleted=False).filter(role__id=role).distinct()
            cwf_main ={}
            for cwf in cwfs:
                cwf_obj = {}
                cwflabel = cwf.name
                cwfcode = cwf.id
                kts = Kt.objects.filter(isdeleted=False).filter(cwf__id = cwf.id).distinct()
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
            stages = Stage.objects.filter(isdeleted=False).filter(role__id=role).distinct()
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
