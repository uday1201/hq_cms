from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from drf_extra_fields.fields import Base64ImageField
from rest_framework import status
from django.http import HttpResponse

from .models import *

class AssessmentSerializer(serializers.ModelSerializer):
    creator = serializers.ModelField(model_field=Assessment._meta.get_field('creator'), default=serializers.CurrentUserDefault(), read_only=True)
    
    created = serializers.ModelField(model_field=Assessment._meta.get_field('created'), read_only=True)
    last_updated = serializers.ModelField(model_field=Assessment._meta.get_field('last_updated'), read_only=True)

    class Meta:
        model = Assessment
        fields = ['id', 'name','problem_statement','qlist','qorder','role','remarks','creator','approved_by','assigned_to','status','isdeleted', 'created', 'last_updated']

class AssessmentProdSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = AssessmentProd
        fields = '__all__'

class AssessmentFinalSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = AssessmentFinal
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    # creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    # last_edited_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    creator = serializers.ModelField(model_field=Question._meta.get_field('creator'), default=serializers.CurrentUserDefault(), read_only=True)
    last_edited_by = serializers.ModelField(model_field=Question._meta.get_field('last_edited_by'), default=serializers.CurrentUserDefault(), read_only=True)

    created = serializers.ModelField(model_field=Question._meta.get_field('created'), read_only=True)
    last_edited = serializers.ModelField(model_field=Question._meta.get_field('last_edited'), read_only=True)


    comments = serializers.JSONField(default=list,read_only=True,required=False)
    qtype_name = serializers.CharField(max_length=100, default="NA", read_only=True)
    related_ques = serializers.JSONField(default=list,read_only=True,required=False)


    class Meta:
        model = Question
        fields = ['id','cwf','kt','stage','exhibits','excels','context','text','qtype','qtype_name','options','score_type','score_weight','creator','role','approved_by','last_edited_by','status','difficulty_level','derivation','org_ques','idealtime','isdeleted','assessmentid','misc','comments','related_ques', 'created', 'last_edited']

    def update(self, instance, validated_data):
        demo = Question.objects.get(pk=instance.id)
        validated_data["last_edited_by"] = self.context['request'].user

        if validated_data.get("cwf") is not None:
            demo.cwf.set(validated_data["cwf"])
            del validated_data["cwf"]

        if validated_data.get("kt") is not None:
            demo.kt.set(validated_data["kt"])
            del validated_data["kt"]

        if validated_data.get("role") is not None:
            demo.role.set(validated_data["role"])
            del validated_data["role"]

        if validated_data.get("assessmentid") is not None:
            demo.assessmentid.set(validated_data["assessmentid"])
            del validated_data["assessmentid"]

        if validated_data.get("exhibits") is not None:
            demo.exhibits.set(validated_data["exhibits"])
            del validated_data["exhibits"]

        if validated_data.get("excels") is not None:
            demo.excels.set(validated_data["excels"])
            del validated_data["excels"]

        #print(validated_data)
        Question.objects.filter(pk=instance.id).update(**validated_data)
        #demo.cwf.add(validated_data["cwf"])
        return demo

class QuestionProdSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuestionProd
        fields = '__all__'

class QuestionFinalSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuestionFinal
        fields = '__all__'

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

    def to_representation(self, instance):
        response = super(ExhibitSerializer, self).to_representation(instance)
        if instance.image:
            response['image'] = instance.image.url
        return response

class ExcelSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Excel
        fields = ['id','file','alt_text','type','isdeleted','creator']

    def create(self, validated_data):
        file=validated_data.pop('file')
        alt_text=validated_data.pop('alt_text')
        return Excel.objects.create(file=file,alt_text=alt_text)

    def to_representation(self, instance):
        response = super(ExcelSerializer, self).to_representation(instance)
        if instance.file:
            response['file'] = instance.file.url
        return response


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
    #email = serializers.EmailField(required=True,validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = User
        fields = ["first_name","last_name", "id","email","access_role","username", "password","isdeleted"]
        extra_kwargs = {
            'username': {'required': True},
            'first_name': {'required': False},
            'last_name': {'required': False}
        }

    def create(self, validated_data):
        permission = self.context['request'].user.access_role
        if permission == "ADMIN":
            user = User.objects.create(
                username=validated_data['username'],
                email=validated_data['email'],
                access_role=validated_data['access_role']
            )

            if validated_data.get('first_name'):
                user.first_name = validated_data['first_name']

            if validated_data.get('last_name'):
                user.last_name = validated_data['last_name']

            user.set_password(validated_data['password'])
            user.save()
            return user
        else:
            raise serializers.ValidationError({"Error": "You are not authorized to do this action"})


class SnippetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Snippet
        fields = '__all__'
