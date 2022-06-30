from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from drf_extra_fields.fields import Base64ImageField

from .models import *

class AssessmentSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Assessment
        fields = ['id', 'name','problem_statement','qlist','role','remarks','creator','approved_by','assigned_to','status','isdeleted']

class QuestionSerializer(serializers.ModelSerializer):
    # assessmentid = serializers.CharField(write_only=True)
    # assessmentid = serializers.ListField(write_only=True,required=False)
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    last_edited_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    comments = serializers.JSONField(default=list,read_only=True,required=False)

    class Meta:
        model = Question
        fields = ['id','cwf','kt','stage','exhibits','excels','context','text','qtype','options','score_type','score_weight','creator','role','approved_by','last_edited_by','status','difficulty_level','idealtime','isdeleted','linked_assessments','misc','comments']

    def update(self, instance, validated_data):
        demo = Question.objects.get(pk=instance.id)
        validated_data["last_edited_by"] = self.context['request'].user
        Question.objects.filter(pk=instance.id).update(**validated_data)
        print(validated_data)
        return demo

    # def create(self, validated_data):
    #     question = Question.objects.create(
    #     stage = validated_data["stage"],
    #     context = validated_data["context"],
    #     text = validated_data["text"],
    #     qtype = validated_data["qtype"],
    #     options = validated_data["options"],
    #     score_type = validated_data["score_type"],
    #     score_weight = validated_data["score_weight"],
    #     # resources = validated_data["resources"],
    #     # approved_by = validated_data["approved_by"],
    #     # last_edited_by = validated_data["last_edited_by"],
    #     status = validated_data["status"],
    #     )
    #
    #     # setting the manytomany fields
    #     question.cwf.set(validated_data["cwf"])
    #     question.kt.set(validated_data["kt"])
    #     question.role.set(validated_data["role"])
    #
    #     # setting excels and exhibits from context {"context" : list(context)} --> [{"type" : <>, "value" : ,"id" :}]
    #     if validated_data["context"] is not None:
    #         context_array = validated_data["context"]["contextList"]
    #         for context in context_array:
    #             if context["type"] == "exhibit":
    #                 question.exhibits.add(context["id"])
    #             if context["type"] == "excel":
    #                 question.excels.add(context["id"])
    #
    #     # saving the question object
    #     obj = question.save()
    #
    #     # adding the question to assessment
    #     assessment_id = validated_data["assessmentid"]
    #     for aid in assessment_id:
    #         Assessment.objects.get(id=aid).qlist.add(question.id)
    #     return question

class RoleSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Role
        fields = '__all__'

class ExhibitSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    image=Base64ImageField()
    class Meta:
        model = Exhibit
        fields = ['id','image','alt_text','type','isdeleted','creator']
    def create(self, validated_data):
        image=validated_data.pop('image')
        alt_text=validated_data.pop('alt_text')
        return Exhibit.objects.create(image=image,alt_text=alt_text)

class ExcelSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Excel
        fields = ['id','file','alt_text','isdeleted','creator']

class CwfSerializer(serializers.ModelSerializer):
    #cwf_creator = serializers.StringRelatedField(default=serializers.CurrentUserDefault(), read_only=True)
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Cwf
        fields = '__all__'
        #extra_kwargs = {'creator': {'default': serializers.CurrentUserDefault(),'read_only':True}}

class KtSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Kt
        fields = '__all__'

class StageSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Stage
        fields = '__all__'

class QtypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Qtype
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Comment
        fields = ['id','author','content','question','mentioned','isdeleted']

class UserSerializer(serializers.ModelSerializer):
    #full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(required=True,validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(write_only=True, required=True,validators=[validate_password])
    class Meta:
        model = User
        fields = ["first_name","last_name", "id","email","access_role","username", "password","isdeleted"]
        extra_kwargs = {
            'username': {'required': True}
        }

    def create(self, validated_data):
        permission = self.context['request'].user.access_role

        if permission == "ADMIN":
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
        else:
            return status.HTTP_401_UNAUTHORIZED

    # def get_full_name(self, obj):
    #     return '{} {}'.format(obj.first_name, obj.last_name)

class SnippetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Snippet
        fields = '__all__'
