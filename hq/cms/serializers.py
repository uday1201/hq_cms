from rest_framework import serializers

from .models import *

class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = '__all__'
        
class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class ExhibitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exhibit
        fields = '__all__'

class ExcelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Excel
        fields = '__all__'

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
        fields = '__all__'
