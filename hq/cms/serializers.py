from rest_framework import serializers

from .models import *

class AssessmentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Assessment
        fields = ['problem_statement','questions','role','remarks','creator','approved_by','last_updated']

class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Question
        fields = ['cwf','kt','stage','exhibits','excels','context','text','qtype','options','score_type','score_weight','resources','creator','role','creator','approved_by','last_edited','last_edited_by']
