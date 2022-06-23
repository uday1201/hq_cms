from rest_framework import serializers

from .models import *

class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = ['problem_statement','questions','role','remarks','creator','approved_by']

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['cwf','kt','stage','exhibits','excels','context','text','qtype','options','score_type','score_weight','resources','creator','role','creator','approved_by','last_edited_by']


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

    class Meta:
        model = User
        fields = ["first_name","last_name", "id","email","access_role","username"]

    # def get_full_name(self, obj):
    #     return '{} {}'.format(obj.first_name, obj.last_name)
