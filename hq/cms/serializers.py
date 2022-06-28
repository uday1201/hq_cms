from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

from .models import *

class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = ['aid','problem_statement','qlist','role','remarks','creator','approved_by','assigned_to','status']

class QuestionSerializer(serializers.ModelSerializer):
    assessmentid = serializers.CharField(write_only=True)
    class Meta:
        model = Question
        fields = ['qid','cwf','kt','stage','exhibits','excels','context','text','qtype','options','score_type','score_weight','resources','creator','role','creator','approved_by','last_edited_by','status','assessmentid']

    def create(self, validated_data):
        question = Question.objects.create(
        stage = validated_data["stage"],
        context = validated_data["context"],
        text = validated_data["text"],
        qtype = validated_data["qtype"],
        options = validated_data["options"],
        score_type = validated_data["score_type"],
        score_weight = validated_data["score_weight"],
        resources = validated_data["resources"],
        creator = validated_data["creator"],
        approved_by = validated_data["approved_by"],
        last_edited_by = validated_data["last_edited_by"],
        status = validated_data["status"],
        )

        # setting the manytomany fields
        question.cwf.set(validated_data["cwf"])
        question.kt.set(validated_data["kt"])
        question.role.set(validated_data["role"])

        # setting excels and exhibits from context {"context" : list(context)} --> [{"type" : <>, "value" : ,"id" :}]
        if validated_data["context"] is not None:
            context_array = validated_data["context"]["context"]
            for context in context_array:
                if context["type"] == "exhibit":
                    question.exhibits.add(context["id"])
                if context["type"] == "excel":
                    question.excels.add(context["id"])

        # saving the question object
        obj = question.save()

        # adding the question to assessment
        assessment_id = validated_data["assessmentid"]
        Assessment.objects.get(aid=assessment_id).qlist.add(question.qid)
        return question

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class ExhibitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exhibit
        fields = ['image','alt_text','type']

class ExcelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Excel
        fields = ['file','alt_text']

class CwfSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cwf
        fields = '__all__'

class KtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kt
        fields = '__all__'

class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = '__all__'

class QtypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Qtype
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['author','content','question','mentioned']

class UserSerializer(serializers.ModelSerializer):
    #full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(required=True,validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(write_only=True, required=True,validators=[validate_password])
    class Meta:
        model = User
        fields = ["first_name","last_name", "id","email","access_role","username", "password"]
        extra_kwargs = {
            'username': {'required': True}
        }

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            access_role=validated_data['access_role']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    # def get_full_name(self, obj):
    #     return '{} {}'.format(obj.first_name, obj.last_name)

class SnippetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Snippet
        fields = '__all__'
