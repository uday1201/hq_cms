from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from drf_extra_fields.fields import Base64ImageField

from .models import *

class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = ['id','name','problem_statement','qlist','role','remarks','creator','approved_by','assigned_to','status']

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id','cwf','kt','stage','exhibits','excels','context','text','qtype','options','score_type','score_weight','resources','creator','role','creator','approved_by','last_edited_by','status','difficulty_level','idealtime']


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class ExhibitSerializer(serializers.ModelSerializer):
    image=Base64ImageField()
    class Meta:
        model = Exhibit
        fields = ['id','image','alt_text','type']
    def create(self, validated_data):
        image=validated_data.pop('image')
        alt_text=validated_data.pop('alt_text')
        return Exhibit.objects.create(image=image,alt_text=alt_text)

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
            last_name=validated_data['last_name']
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
