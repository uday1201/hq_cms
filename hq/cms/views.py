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
import random
import string
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated, IsAdminUser, BasePermission, SAFE_METHODS, AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import authentication_classes, permission_classes
import subprocess
import os

# token authentication custom oveeride
@authentication_classes([])
@permission_classes([])
class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        print(request)
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

        if "status" in request.GET:
            status = request.GET.getlist('status')
            if status:
                queryset = queryset.filter(status__in=status)

        if "code" in request.GET:
            code = request.GET.getlist('code')
            if code:
                queryset = queryset.filter(code__in=code)

        if "creator" in request.GET:
            created_by = request.GET.getlist('creator')
            if created_by:
                queryset = queryset.filter(creator__in=created_by)

        if "role" in request.GET:
            role = request.GET.getlist('role')
            if role:
                queryset = queryset.filter(role__in=role)

        if "starttime" in request.GET and "endtime" in request.GET:
            queryset = queryset.filter(created__range=[request.GET["starttime"],request.GET["endtime"]]).distinct()
        #FIXME - Correct filtering in this
        elif "starttime" in request.GET:
            queryset = queryset.filter(created__gte=request.GET["starttime"]).distinct()
        elif "endtime" in request.GET:
            queryset = queryset.filter(created__lte=request.GET["endtime"]).distinct()

        queryset_order = queryset.order_by('-last_updated')
        serializer = AssessmentSerializer(queryset_order, many=True)
        page = self.paginate_queryset(serializer.data)
        return Response(page)


class Logout(APIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']
    def get(self, request):
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
            comments.append(
                {
                    "id" : comment.id,
                    "author" : comment.author.username,
                    "content" : comment.content,
                    "date_posted": comment.date_posted
                }
            )
        q.comments = comments
    return queryset

# function to get qtypename
def get_qtype(queryset):
    # get the qtype name
    for q in queryset:
        for qtype in Qtype.objects.filter(qtype_id = q.qtype.qtype_id):
            q.qtype_name = qtype.name
    return queryset

# function to get related questions
def related_questions(queryset):
    for q in queryset:
        if q.derivation == "DERIVED":
            q.related_ques = [q.org_ques.id]
            # return siblings too
        else:
            rlist = []
            rqs = Question.objects.filter(org_ques=q.id)
            for rq in rqs:
                rlist.append(rq.id)
            q.related_ques = rlist
        print("uuu",q.related_ques)
    return queryset


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.filter(isdeleted=False)
    queryset = queryset.order_by('-last_edited')
    serializer_class = QuestionSerializer
    pagination_class = QuestionSetPagination
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        queryset = Question.objects.filter(isdeleted=False)

        user = authenticate_token(self, request)
        # filtering from the user
        assessment_queryset = Assessment.objects.filter(Q(creator=user["user_id"]) | Q(assigned_to=user["user_id"]))
        assessments = []
        for a in assessment_queryset:
            assessments.append(a.id)

        if user["role"] != "ADMIN":
            queryset = queryset.filter(Q(creator=user["user_id"]) | Q(assessmentid__in=assessments))

        if "assessmentid" in request.GET:
            # queryset = queryset.filter(assessmentid= request.GET["assessmentid"]).distinct()
            assessment = request.GET.getlist('assessmentid')
            if assessment:
                queryset = queryset.filter(assessmentid__in=assessment)

        if "cwf" in request.GET:
            # queryset = queryset.filter(cwf=request.GET["cwf"]).distinct()
            cwf = request.GET.getlist('cwf')
            if cwf:
                queryset = queryset.filter(cwf__in=cwf)

        if "kt" in request.GET:
            # queryset = queryset.filter(kt=request.GET["kt"]).distinct()
            kt = request.GET.getlist('kt')
            if kt:
                queryset = queryset.filter(kt__in=kt)

        if "created_by" in request.GET:
            # queryset = queryset.filter(creator = request.GET["created_by"]).distinct()
            creator = request.GET.getlist('created_by')
            if creator:
                queryset = queryset.filter(creator__in=creator)

        if "role" in request.GET:
            # queryset = queryset.filter(role=request.GET["role"]).distinct()
            role = request.GET.getlist('role')
            if role:
                queryset = queryset.filter(role__in=role)

        if "code" in request.GET:
            code = request.GET.getlist('code')
            if code:
                queryset = queryset.filter(code__in=code)

        if "starttime" in request.GET and "endtime" in request.GET:
            queryset = queryset.filter(created__range=[request.GET["starttime"],request.GET["endtime"]]).distinct()
        #FIXME - Correct filtering in this
        elif "starttime" in request.GET:
            queryset = queryset.filter(created__gte=request.GET["starttime"]).distinct()
        elif "endtime" in request.GET:
            queryset = queryset.filter(created__lte=request.GET["endtime"]).distinct()

        # return comments linked to the questions
        queryset = get_comments(queryset)
        # get the qtype name
        queryset = get_qtype(queryset)
        # get the related questions
        queryset = related_questions(queryset)
        # realted question filter
        if "related_ques" in request.GET:
            related_ques = request.GET.get('related_ques')
            if related_ques:
                queryset = queryset.filter(related_ques__in=related_ques)
        serializer = QuestionSerializer(queryset, many=True)
        page = self.paginate_queryset(serializer.data)
        return Response(page)

    def retrieve(self, request, pk=None):
        queryset = Question.objects.filter(isdeleted=False).filter(id=pk)
        #check the user rights
        user = authenticate_token(self, request)
        # get asessments
        assessment_queryset = Assessment.objects.filter(Q(creator=user["user_id"]) | Q(assigned_to=user["user_id"]))
        assessments = []
        for a in assessment_queryset:
            assessments.append(a.id)
        # check the condition to return the question
        for question in queryset:
            qassessments = []
            for qassessment in question.assessmentid.all():
                qassessments.append(qassessment.id)
            if question.creator.id == user["user_id"] or len(set(qassessments) & set(assessments)) != 0 or user['role'] == 'ADMIN':
                flag = True
            else:
                flag = False

        # return comments linked to the question
        queryset = get_comments(queryset)
        # get the qtype name
        queryset = get_qtype(queryset)
        # get the related questions
        queryset = related_questions(queryset)
        if flag:
            serializer = QuestionSerializer(queryset, many=True)
            return Response(serializer.data[0])
        else:
            return Response({"Not Authorized": "You don't have access to this entry"},status=status.HTTP_401_UNAUTHORIZED)

class AssessmentProdViewSet(viewsets.ModelViewSet):
    queryset = AssessmentProd.objects.filter(isdeleted=False).order_by('-last_updated')
    serializer_class = AssessmentProdSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']

class QuestionProdViewSet(viewsets.ModelViewSet):
    queryset = QuestionProd.objects.filter(isdeleted=False).order_by('-created')
    serializer_class = QuestionProdSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']

class AssessmentFinalViewSet(viewsets.ModelViewSet):
    queryset = AssessmentFinal.objects.filter(isdeleted=False).order_by('-last_updated')
    serializer_class = AssessmentFinalSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']

class QuestionFinalViewSet(viewsets.ModelViewSet):
    queryset = QuestionFinal.objects.filter(isdeleted=False).order_by('-created')
    serializer_class = QuestionFinalSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']

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
    queryset = Qtype.objects.all().order_by('-code')
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
        queryset = User.objects.filter(isdeleted=False).order_by('-id')
        if user["role"] == "MEMBER":
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
                # id = "dummyid11",
                id = ''.join(random.choices(string.ascii_lowercase, k=5)),
                name = valid_data["role"].get("label"),
                creator = user
            )
            print(user)
            role.save()
            role_id = role.id
            print(role_id)
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
                    # id = "dummyid11",
                    id = ''.join(random.choices(string.ascii_lowercase, k=5)),
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
                    # id = "dummyid11",
                    id = ''.join(random.choices(string.ascii_lowercase, k=5)),
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
                        # id = "dummyid11",
                        id = ''.join(random.choices(string.ascii_lowercase, k=5)),
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


class CopyQuestion(APIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post']

#request -  {
#   copyQuestion: JSON-copyQuestion,
#   assessmentId: assessmentId,
#   questionId: params.questionId,
# }
    def post(self, request):
        reqs = request.body.decode('utf-8')
        data = json.loads(reqs)
        ques_id = data["questionId"]
        if "assessmentId" in data:
            a_id = data["assessmentId"]
        valid_data = data["copyQuestion"]

        access_token = request.headers['Authorization'].split(" ")[-1]
        user=Token.objects.get(key=access_token).user

        org_ques = Question.objects.filter(id=ques_id)


        derived_ques = Question(
            # code = valid_data["code"],
            code = "",
            #stage = valid_data["stage"],
            context = valid_data["context"],
            text = valid_data["text"],
            #qtype = valid_data["qtype"],
            options = valid_data["options"],
            score_weight = valid_data["score_weight"],
            # setting the creator and editor as the current user
            creator = user,
            last_edited_by = user,
            idealtime = valid_data["idealtime"],
            difficulty_level = valid_data["difficulty_level"],
            misc = valid_data["misc"],
            # setting the assessment as the current one
            # status = valid_data["status"],
            status = "DEV",
            # setting it as derived question and original question relationship
            derivation = "DERIVED",
            #org_ques = q
        )

        # For loop not required
        if valid_data["qtype"] is not None:
            for q in Qtype.objects.filter(qtype_id=valid_data["qtype"]):
                derived_ques.qtype = q

        if valid_data["stage"] is not None:
            for s in Stage.objects.filter(id=valid_data["stage"]):
                derived_ques.stage = s

        for q in org_ques:
            if "assessmentId" in data:
                q.assessmentid.remove(a_id)
            # check if the inherited question is from original
            if q.derivation == "DERIVED":
                derived_ques.org_ques = q.org_ques
            else:
                derived_ques.org_ques = q

        derived_ques.save()
        derived_ques.cwf.set(valid_data["cwf"])
        derived_ques.kt.set(valid_data["kt"])
        derived_ques.role.set(valid_data["role"])
        if 'skills' in valid_data:
            derived_ques.skills.set(valid_data["skills"])
        if 'subskill' in valid_data:
            derived_ques.subskill.set(valid_data["subskill"])
        derived_ques.exhibits.set(valid_data["exhibits"])
        derived_ques.excels.set(valid_data["excels"])

        if "assessmentId" in data:
            derived_ques.assessmentid.set([a_id])

            for a in Assessment.objects.filter(id=a_id):
                qlist = a.qorder
                if ques_id in qlist:
                    qlist[qlist.index(ques_id)] = derived_ques.id
                else:
                    qlist.append(derived_ques.id)
                a.qorder = qlist
                a.save()

        queryset = Question.objects.filter(id=derived_ques.id)
        serializer = QuestionSerializer(queryset, many=True)
        return Response(serializer.data)

class MoveToProd(APIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post']


    def post(self, request):
        reqs = request.body.decode('utf-8')
        data = json.loads(reqs)

        access_token = request.headers['Authorization'].split(" ")[-1]
        user=Token.objects.get(key=access_token).user

        response = {}

        if "assessmentId" in data:
            aid = data["assessmentId"]

            for a in Assessment.objects.filter(id=aid):
                if a.status == "READY":
                    prod_entry = AssessmentProd(
                        code = a.code,
                        problem_statement = a.problem_statement,
                        name = a.name,
                        # how to connect qlist dev to prod
                        #qlist = a.qlist,
                        #qorder = a.qorder,
                        role = a.role,
                        remarks = a.remarks,
                        creator = a.creator,
                        approved_by = a.approved_by,
                        #assigned_to = self.assigned_to,
                        isdeleted = a.isdeleted
                    )

                    prod_entry.save()

                    #setting qlist to prod questions only
                    dev_qlist = a.qlist.all()
                    prod_qlist = []
                    for q in dev_qlist:
                        if q.status == "PROD":
                            prod_qlist.append(q.prodques)
                    prod_entry.qlist.set(prod_qlist)

                    # setting qorder
                    prod_order = []
                    for o in a.qorder:
                        for oq in Question.objects.filter(id=o):
                            if oq.prodques is not None:
                                if oq.prodques in prod_qlist:
                                    prod_order.append(oq.prodques.id)
                    prod_entry.qorder = prod_order
                    prod_entry.save()

                    # setting the prod question
                    a.prod = prod_entry
                    a.status = "PROD"
                    a.save()

                    response["Prod Assessment id"] = prod_entry.id

                elif a.status == "APPROVED":
                    for prod in AssessmentProd.objects.filter(id = a.prod):
                        prod.code = a.code
                        prod.problem_statement = a.problem_statement,
                        prod.name = a.name,
                        # how to connect qlist dev to prod
                        #prod.qlist = a.qlist,
                        #prod.qorder = a.qorder,
                        prod.role = a.role,
                        prod.remarks = a.remarks,
                        prod.creator = a.creator,
                        prod.approved_by = a.approved_by,
                        #assigned_to = self.assigned_to,
                        prod.isdeleted = a.isdeleted

                        #setting qlist to prod questions only
                        dev_qlist = a.qlist.all()
                        prod_qlist = []
                        for q in dev_qlist:
                            if q.status == "PROD":
                                prod_qlist.append(q.prodques)
                        prod.qlist.set(prod_qlist)

                        # setting qorder
                        prod_order = []
                        for o in a.qorder:
                            for oq in Question.objects.filter(id=o):
                                if oq.prodques is not None:
                                    if oq.prodques in prod_qlist:
                                        prod_order.append(oq.prodques.id)
                        prod.qorder = prod_order

                        prod.save()

                        # setting the prod question
                        a.prod = prod
                        a.status = "PROD"
                        a.save()

                        response["Prod Assessment id"] = prod.id

                elif a.status == "REJECTED":
                    for prod in AssessmentProd.objects.filter(id = a.prod):
                        a.code = prod.code
                        a.problem_statement = prod.problem_statement,
                        a.name = prod.name,
                        # how to connect qlist dev to prod
                        a.qlist = prod.qlist,
                        #a.qorder = prod.qorder,
                        a.role = prod.role,
                        a.remarks = prod.remarks,
                        a.creator = prod.creator,
                        a.approved_by = prod.approved_by,
                        #assigned_to = self.assigned_to,
                        a.isdeleted = prod.isdeleted

                        #reverting qlist from prod questions
                        dev_qlist = []
                        prod_qlist = prod.qlist.all()
                        for q in prod_qlist:
                            for qid in Question.objects.filter(prodques=q):
                                dev_qlist.append(qid.id)
                        a.qlist.set(dev_qlist)

                        # setting qorder
                        dev_order = []
                        for o in prod.qorder:
                            for oq in Question.objects.filter(prodques=o):
                                if oq is not None:
                                    if oq in dev_qlist:
                                        dev_order.append(oq.id)
                        a.qorder = dev_order
                        a.save()

                        response["Dev revert Assessment id"] = a.id

                else:
                    return Response({"failure": "Status not apropriate for the transaction"},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)



        if "questionId" in data:
            ques_id = data["questionId"]

            for q in Question.objects.filter(id=ques_id):
                if q.status == "READY":
                    prod = QuestionProd(
                        code = q.code,
                        context = q.context,
                        text = q.text,
                        options = q.options,
                        score_weight = q.score_weight,
                        creator = user,
                        idealtime = q.idealtime,
                        difficulty_level = q.difficulty_level,
                        misc = q.misc,
                        qtype = q.qtype,
                        stage = q.stage
                    )

                    prod.save()
                    prod.cwf.set(q.cwf.all())
                    prod.kt.set(q.kt.all())
                    prod.role.set(q.role.all())
                    prod.skills.set(q.skills.all())
                    prod.subskill.set(q.subskill.all())
                    prod.exhibits.set(q.exhibits.all())
                    prod.excels.set(q.excels.all())

                    # assessment id
                    prod.assessmentiddev.set(q.assessmentid.all())
                    prod_ass = []
                    for ass in prod.assessmentiddev.all():
                        for a in Assessment.objects.filter(id=ass.id):
                            if a.status == "PROD":
                                prod_ass.append(a.prod)
                    prod.assessmentidprod.set(prod_ass)

                    # setting prod question
                    q.prodques = prod

                    # setting the dev question to prod
                    q.status = "PROD"

                    q.save()

                    response["Prod Question id"] = prod.id

                elif q.status == "APPROVED":
                    for prod in AssessmentProd.objects.filter(id = a.prod):
                        prod.code = q.code
                        prod.context = q.context
                        prod.text = q.text
                        prod.options = q.options
                        prod.score_weight = q.score_weight
                        prod.creator = user
                        prod.idealtime = q.idealtime
                        prod.difficulty_level = q.difficulty_level
                        prod.misc = q.misc
                        prod.qtype = q.qtype
                        prod.stage = q.stag

                        prod.cwf.set(q.cwf.all())
                        prod.kt.set(q.kt.all())
                        prod.role.set(q.role.all())
                        prod.skills.set(q.skills.all())
                        prod.subskill.set(q.subskill.all())
                        prod.exhibits.set(q.exhibits.all())
                        prod.excels.set(q.excels.all())

                        # assessment id
                        prod.assessmentiddev.set(q.assessmentid.all())
                        prod_ass = []
                        for ass in prod.assessmentiddev.all():
                            for a in Assessment.objects.filter(id=ass.id):
                                if a.status == "PROD":
                                    prod_ass.append(a.prod)
                        prod.assessmentidprod.set(prod_ass)

                        # setting prod question
                        q.prodques = prod

                        # setting the dev question to prod
                        q.status = "PROD"

                        prod.save()
                        q.save()

                        response["Prod Question id"] = prod.id

                elif q.status == "REJECTED":
                    for prod in AssessmentProd.objects.filter(id = a.prod):
                        q.code = prod.code
                        q.context = prod.context
                        q.text = prod.text
                        q.options = prod.options
                        q.score_weight = prod.score_weight
                        q.creator = user
                        q.idealtime = prod.idealtime
                        q.difficulty_level = prod.difficulty_level
                        q.misc = prod.misc
                        q.status = prod.status
                        q.qtype = prod.qtype
                        q.stage = prod.stag

                        q.cwf.set(prod.cwf.all())
                        q.kt.set(prod.kt.all())
                        q.role.set(prod.role.all())
                        q.skills.set(prod.skills.all())
                        q.subskill.set(prod.subskill.all())
                        q.exhibits.set(prod.exhibits.all())
                        q.excels.set(prod.excels.all())
                        # assessment id
                        q.assessmentid.set(prod.assessmentiddev.all())

                        q.save()

                        # setting the dev question to prod
                        q.status = "To be reviewed"

                        response["Dev revert Question id"] = q.id

                    else:
                        return Response({"failure": "Status not apropriate for the transaction"},
                                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(response)


class MigrateDBProd(APIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post']


    def post(self, request):
        reqs = request.body.decode('utf-8')
        data = json.loads(reqs)

        access_token = request.headers['Authorization'].split(" ")[-1]
        user=Token.objects.get(key=access_token).user

        if user.access_role == 'ADMIN':
            if data["rollback"]:
                out = os.system('bash rollback.sh')
            else:
                out = os.system('bash migrate.sh')
            # error handling
            if out == 0:
                return Response({"Success":out},status=status.HTTP_200_OK)
            else:
                return Response({"Error":out},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"Not Authorized": "You don't have access to this entry"},status=status.HTTP_401_UNAUTHORIZED)


class MoveToFinal(APIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post']


    def post(self, request):
        reqs = request.body.decode('utf-8')
        data = json.loads(reqs)

        access_token = request.headers['Authorization'].split(" ")[-1]
        user=Token.objects.get(key=access_token).user

        response = {}

        if "assessmentId" in data:
            aid = data["assessmentId"]
            qlist = []
            qorder = []
            newid = None
            exists = False
            prod_qlist =[]
            prod_order = []
            for a in AssessmentProd.objects.filter(id=aid):
                if a.final is not None:
                    exists = True
                qlist = a.qlist
                qorder = a.qorder

                if exists:
                    final_entry = AssessmentFinal(
                        code = a.code,
                        problem_statement = a.problem_statement,
                        name = a.name,
                        # how to connect qlist dev to prod
                        #qlist = a.qlist,
                        #qorder = a.qorder,
                        role = a.role,
                        remarks = a.remarks,
                        creator = a.creator,
                        approved_by = user,
                        isdeleted = a.isdeleted
                    )
                    # setting the final question
                    a.final = final_entry
                    a.save()
                    final_entry.save()
                    newid = final_entry.id

                else:
                    for final in AssessmentFinal.objects.filter(id = a.final):
                        final.code = a.code
                        final.problem_statement = a.problem_statement,
                        final.name = a.name,
                        final.role = a.role,
                        final.remarks = a.remarks,
                        final.creator = a.creator,
                        final.approved_by = a.approved_by,
                        final.isdeleted = a.isdeleted
                        newid = a.final

                        final.save()

                for qid in qorder:
                    for q in QuestionProd.objects.filter(id=qid):
                        if q.finalques is None:
                            final = QuestionProd(
                                code = q.code,
                                context = q.context,
                                text = q.text,
                                options = q.options,
                                score_weight = q.score_weight,
                                creator = user,
                                idealtime = q.idealtime,
                                difficulty_level = q.difficulty_level,
                                misc = q.misc,
                                qtype = q.qtype,
                                stage = q.stage
                            )

                            final.save()
                            final.cwf.set(q.cwf.all())
                            final.kt.set(q.kt.all())
                            final.role.set(q.role.all())
                            final.skills.set(q.skills.all())
                            final.subskill.set(q.subskill.all())
                            final.exhibits.set(q.exhibits.all())
                            final.excels.set(q.excels.all())

                            final.finalques = final

                            final.save()

                            prod_qlist.append(final)
                            prod_order.append(final.id)

                        else:
                            for final in QuestionFinal.objects.filter(id=q.finalques):
                                final.code = q.code
                                final.context = q.context
                                final.text = q.text
                                final.options = q.options
                                final.score_weight = q.score_weight
                                final.creator = user
                                final.idealtime = q.idealtime
                                final.difficulty_level = q.difficulty_level
                                final.misc = q.misc
                                final.qtype = q.qtype
                                final.stage = q.stag

                                final.cwf.set(q.cwf.all())
                                final.kt.set(q.kt.all())
                                final.role.set(q.role.all())
                                final.skills.set(q.skills.all())
                                final.subskill.set(q.subskill.all())
                                final.exhibits.set(q.exhibits.all())
                                final.excels.set(q.excels.all())

                                final.save()

                                prod_qlist.append(final)
                                prod_order.append(final.id)

            queryset = AssessmentFinal.objects.filter(id=newid)
            for fa in queryset:
                fa.qlist = prod_qlist
                fa.qorder= prod_order
                fa.save()

            serializer = AssessmentFinal(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({"Error": "No assessmentId given"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class SnippetViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
