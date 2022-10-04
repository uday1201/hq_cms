from django.db import models
from django.core.validators import MinValueValidator
from datetime import datetime
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField



# Create your models here.
class AssessmentFinal(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=20, unique=True)
    problem_statement = models.CharField(max_length=1000, blank = True)
    name = models.CharField(max_length=100, blank = True)
    qlist = models.ManyToManyField("Questionfinal",blank=True, related_name='finalassessments')
    qorder = models.JSONField(default=list, blank=True)
    role = models.ForeignKey("Role", on_delete = models.SET_NULL, null=True, related_name='finalassessment_role') # if the creator user is deleted it will set this field to NULL
    remarks = models.CharField(max_length=1000, blank = True)
    # timestamp and tracking
    creator = models.ForeignKey("User", on_delete = models.SET_NULL, null=True, related_name='finalassessment_creator') # if the creator user is deleted it will set this field to NULL
    approved_by = models.ForeignKey("User", on_delete = models.SET_NULL, null=True, blank=True,related_name='finalassessment_approver') # if the user is deleted it will set this field to NULL
    last_updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    # deleted field
    isdeleted = models.BooleanField(blank=True, default=False)


    def __str__(self):
        return self.name


class AssessmentProd(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=20, unique=True)
    problem_statement = models.CharField(max_length=1000, blank = True)
    name = models.CharField(max_length=100, blank = True)
    qlist = models.ManyToManyField("QuestionProd",blank=True, related_name='assessments')
    qorder = models.JSONField(default=list, blank=True)
    role = models.ForeignKey("Role", on_delete = models.SET_NULL, null=True, related_name='prodassessment_role') # if the creator user is deleted it will set this field to NULL
    remarks = models.CharField(max_length=1000, blank = True)
    # timestamp and tracking
    creator = models.ForeignKey("User", on_delete = models.SET_NULL, null=True, related_name='prodassessment_creator') # if the creator user is deleted it will set this field to NULL
    approved_by = models.ForeignKey("User", on_delete = models.SET_NULL, null=True, blank=True,related_name='prodassessment_approver') # if the user is deleted it will set this field to NULL
    last_updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    # deleted field
    isdeleted = models.BooleanField(blank=True, default=False)
    # final assessment
    final = models.ForeignKey("AssessmentFinal", on_delete= models.SET_NULL, null=True, blank=True, related_name = "final_assessment")



    def __str__(self):
        return self.name

class Assessment(models.Model):
    ASSESSMENT_STATUS_CHOICES = (
    ("DEV", "In development"),
    ("READY", "Ready"),
    ("PROD", "In Production"),
    ("UPDATED", "Updated"),
    ("APPROVED", "Approved"),
    ("REJECTED", "Rejected"),
    ("REVIEW", "To be reviewed")
    )

    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=20)
    problem_statement = models.CharField(max_length=1000, blank = True)
    name = models.CharField(max_length=100, blank = True)
    qlist = models.ManyToManyField("Question",blank=True, related_name='devassessments')
    qorder = models.JSONField(default=list, blank=True)
    role = models.ForeignKey("Role", on_delete = models.SET_NULL, null=True, related_name='devassessment_role') # if the creator user is deleted it will set this field to NULL
    remarks = models.CharField(max_length=1000, blank = True)
    # timestamp and tracking
    creator = models.ForeignKey("User", on_delete = models.SET_NULL, null=True, related_name='devassessment_creator') # if the creator user is deleted it will set this field to NULL
    approved_by = models.ForeignKey("User", on_delete = models.SET_NULL, null=True, blank=True,related_name='devassessment_approver') # if the user is deleted it will set this field to NULL
    last_updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    assigned_to = models.ManyToManyField("User", blank=True, related_name='devassessment_assignedto')
    # deleted field
    isdeleted = models.BooleanField(blank=True, default=False)
    # setting status for the in dev question
    status = models.CharField(max_length=20, choices = ASSESSMENT_STATUS_CHOICES, default = "DEV")
    # prod assessment
    prod = models.ForeignKey("AssessmentProd", on_delete= models.SET_NULL, null=True, blank=True, related_name = "prod_assessment")

    def __str__(self):
        return self.name

class QuestionFinal(models.Model):

    DIFFICULTY_CHOICES = (
    ("EASY", "EASY"),
    ("MEDIUM", "MEDIUM"),
    ("HARD", "HARD"),
    )
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=20, unique=True)
    # details of the question
    cwf = models.ManyToManyField("Cwf",blank=True) # for ManyToManyField Django will automatically create a table to manage to manage many-to-many relationships
    kt = models.ManyToManyField("Kt",blank=True)
    role = models.ManyToManyField("Role",blank=True)
    stage = models.ForeignKey("Stage", on_delete = models.SET_NULL, null=True, blank=True) # if the stage id is delelted it will set this field to NULL
    skills =models.ManyToManyField("Skill",blank=True)
    subskill = models.ManyToManyField("SubSkill",blank=True)
    # assests for the question
    exhibits = models.ManyToManyField("Exhibit", blank=True)
    excels = models.ManyToManyField("Excel", blank=True)
    # context = ArrayField(
    #         models.JSONField(blank=True, null=True),
    #         size=10,
    #         blank=True,
    #         null=True
    #     )
    context = models.JSONField(default=list, blank=True)
    # content of the question
    text = models.CharField(max_length = 100, blank = False, null = False)
    qtype = models.ForeignKey("Qtype", on_delete = models.SET_NULL, null=True)
    options = models.JSONField(blank=True, null=True)
    score_type = models.CharField(max_length = 10, blank = False, null = False)
    score_weight = models.FloatField(validators = [MinValueValidator(0)])
    # extras
    # resources = models.JSONField(blank=True, null=True)
    # timestamp and tracking
    creator = models.ForeignKey("User", on_delete = models.SET_NULL, null=True, related_name='finalquestion_creator') # if the creator user is deleted it will set this field to NULL
    approved_by = models.ForeignKey("User", on_delete = models.SET_NULL, null=True, blank =True, related_name='finalquestion_approver') # if the user is deleted it will set this field to NULL
    #last_edited_by = models.ForeignKey("User", on_delete = models.SET_NULL, null=True, blank=True, related_name='question_editor') # if the user is deleted it will set this field to NULL
    #last_edited = models.DateTimeField(auto_now =True)
    created = models.DateTimeField(auto_now_add =True)
    # miscellaneous fields
    idealtime = models.FloatField(blank=True, null=True)
    difficulty_level = models.CharField(max_length=50, choices=DIFFICULTY_CHOICES, blank=True, null=True, default="MEDIUM")
    misc = models.JSONField(blank=True, null=True)
    # deleted field
    isdeleted = models.BooleanField(blank=True, default=False)
    # bidirectional ManyToManyField
    assessmentidfinal = models.ManyToManyField('AssessmentFinal', through = AssessmentFinal.qlist.through, blank=True)

    def __str__(self):
        return str(self.id)

class QuestionProd(models.Model):

    DIFFICULTY_CHOICES = (
    ("EASY", "EASY"),
    ("MEDIUM", "MEDIUM"),
    ("HARD", "HARD"),
    )
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=20, unique=True)
    # details of the question
    cwf = models.ManyToManyField("Cwf",blank=True) # for ManyToManyField Django will automatically create a table to manage to manage many-to-many relationships
    kt = models.ManyToManyField("Kt",blank=True)
    role = models.ManyToManyField("Role",blank=True)
    stage = models.ForeignKey("Stage", on_delete = models.SET_NULL, null=True, blank=True) # if the stage id is delelted it will set this field to NULL
    skills =models.ManyToManyField("Skill",blank=True)
    subskill = models.ManyToManyField("SubSkill",blank=True)
    # assests for the question
    exhibits = models.ManyToManyField("Exhibit", blank=True)
    excels = models.ManyToManyField("Excel", blank=True)
    # context = ArrayField(
    #         models.JSONField(blank=True, null=True),
    #         size=10,
    #         blank=True,
    #         null=True
    #     )
    context = models.JSONField(default=list, blank=True)
    # content of the question
    text = models.CharField(max_length = 100, blank = False, null = False)
    qtype = models.ForeignKey("Qtype", on_delete = models.SET_NULL, null=True)
    options = models.JSONField(blank=True, null=True)
    score_type = models.CharField(max_length = 10, blank = False, null = False)
    score_weight = models.FloatField(validators = [MinValueValidator(0)])
    # extras
    # resources = models.JSONField(blank=True, null=True)
    # timestamp and tracking
    creator = models.ForeignKey("User", on_delete = models.SET_NULL, null=True, related_name='question_creator') # if the creator user is deleted it will set this field to NULL
    approved_by = models.ForeignKey("User", on_delete = models.SET_NULL, null=True, blank =True, related_name='question_approver') # if the user is deleted it will set this field to NULL
    #last_edited_by = models.ForeignKey("User", on_delete = models.SET_NULL, null=True, blank=True, related_name='question_editor') # if the user is deleted it will set this field to NULL
    #last_edited = models.DateTimeField(auto_now =True)
    created = models.DateTimeField(auto_now_add =True)
    # miscellaneous fields
    idealtime = models.FloatField(blank=True, null=True)
    difficulty_level = models.CharField(max_length=50, choices=DIFFICULTY_CHOICES, blank=True, null=True, default="MEDIUM")
    misc = models.JSONField(blank=True, null=True)
    # deleted field
    isdeleted = models.BooleanField(blank=True, default=False)
    # bidirectional ManyToManyField
    assessmentiddev = models.ManyToManyField('Assessment', blank=True)
    assessmentidprod = models.ManyToManyField('AssessmentProd', through = AssessmentProd.qlist.through, blank=True)
    # final question
    finalques = models.ForeignKey("QuestionFinal", on_delete= models.SET_NULL, null=True, blank=True, related_name = "prod_question")

    def __str__(self):
        return str(self.id)

class Question(models.Model):
    QUESTION_STATUS_CHOICES = (
    ("DEV", "In development"),
    ("READY", "Ready"),
    ("PROD", "In Production"),
    ("UPDATED", "Updated"),
    ("APPROVED", "Approved"),
    ("REJECTED", "Rejected"),
    ("REVIEW", "To be reviewed")
    )

    DIFFICULTY_CHOICES = (
    ("EASY", "EASY"),
    ("MEDIUM", "MEDIUM"),
    ("HARD", "HARD"),
    )

    DERIVATION = (
    ("MASTER", "Master"),
    ("DERIVED", "Derived")
    )

    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=20)
    # details of the question
    cwf = models.ManyToManyField("Cwf",blank=True) # for ManyToManyField Django will automatically create a table to manage to manage many-to-many relationships
    kt = models.ManyToManyField("Kt",blank=True)
    role = models.ManyToManyField("Role",blank=True)
    stage = models.ForeignKey("Stage", on_delete = models.SET_NULL, null=True, blank=True) # if the stage id is delelted it will set this field to NULL
    skills =models.ManyToManyField("Skill",blank=True)
    subskill = models.ManyToManyField("SubSkill",blank=True)
    # assests for the question
    exhibits = models.ManyToManyField("Exhibit", blank=True)
    excels = models.ManyToManyField("Excel", blank=True)
    context = models.JSONField(default=list, blank=True)
    # content of the question
    text = models.TextField(blank = False, null = False)
    qtype = models.ForeignKey("Qtype", on_delete = models.SET_NULL, null=True)
    options = models.JSONField(blank=True, null=True)
    score_type = models.CharField(max_length = 10, blank = False, null = False)
    score_weight = models.FloatField(validators = [MinValueValidator(0)])
    # extras
    # timestamp and tracking
    creator = models.ForeignKey("User", on_delete = models.SET_NULL, null=True, related_name='devquestion_creator') # if the creator user is deleted it will set this field to NULL
    approved_by = models.ForeignKey("User", on_delete = models.SET_NULL, null=True, blank =True, related_name='devquestion_approver') # if the user is deleted it will set this field to NULL
    last_edited_by = models.ForeignKey("User", on_delete = models.SET_NULL, null=True, blank=True, related_name='devquestion_editor') # if the user is deleted it will set this field to NULL
    last_edited = models.DateTimeField(auto_now =True)
    created = models.DateTimeField(auto_now_add =True)
    # miscellaneous fields
    idealtime = models.FloatField(blank=True, null=True)
    difficulty_level = models.CharField(max_length=50, choices=DIFFICULTY_CHOICES, blank=True, null=True, default="MEDIUM")
    misc = models.JSONField(blank=True, null=True)
    # deleted field
    isdeleted = models.BooleanField(blank=True, default=False)
    # bidirectional ManyToManyField
    assessmentid = models.ManyToManyField('Assessment', through = Assessment.qlist.through, blank=True)


    # setting status for the in dev question
    status = models.CharField(max_length=20, choices = QUESTION_STATUS_CHOICES, default = "DEV")
    # prod question
    prodques = models.ForeignKey("QuestionProd", on_delete= models.SET_NULL, null=True, blank=True, related_name = "prod_question")
    # master and derived question
    derivation = models.CharField(max_length=20, choices = DERIVATION, default = "MASTER")
    org_ques = models.ForeignKey("Question", on_delete = models.SET_NULL, null=True, blank=True, related_name='original_question')

    def __str__(self):
        return str(self.id)



class Role(models.Model):
    #role_id = models.AutoField(primary_key=True)
    id = models.CharField(max_length = 20, primary_key=True)
    name = models.CharField(max_length = 100, blank = False)
    creator = models.ForeignKey("User", on_delete = models.SET_NULL, null=True, related_name='role_creator')
    # deleted field
    isdeleted = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return self.name

def exhibit_upload_to(instance, filename):
    return 'exhibits/{filename}'.format(filename=filename)

class Exhibit(models.Model):
    id = models.AutoField(primary_key=True)
    # we have 2 choices here, if we want to store the assests externally on the cloud we need to have a URL field, otherwise we can also use Django media manager with imagefield
    #url = models.URLField(max_length = 250)
    #file = models.FileField(upload_to = 'exhibits/')
    image = models.ImageField(upload_to = exhibit_upload_to, blank=True)
    alt_text = models.CharField(max_length = 100, blank = True)
    type = models.CharField(max_length = 100, blank = True, default="exhibit")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey("User", on_delete = models.SET_NULL, null=True, related_name='exhibit_creator')
    # deleted field
    isdeleted = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return self.alt_text

def file_upload_to(instance, filename):
    return 'files/{filename}'.format(filename=filename)

class Excel(models.Model):
    id = models.AutoField(primary_key=True)
    #url = models.URLField(max_length = 250)
    file = models.FileField(upload_to = file_upload_to, blank=True)
    type = models.CharField(max_length = 100, blank = True, default="any file")
    alt_text = models.CharField(max_length = 100, blank = True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey("User", on_delete = models.SET_NULL, null=True, related_name='excel_creator')
    # deleted field
    isdeleted = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return self.alt_text


# for the users we can also use the Django's inbuilt user management system
# we will use the inbuilt one
class User(AbstractUser):
    ROLE_CHOICES = (
    ('MEMBER','Member'),
    ('ADMIN','Admin')
    )
    email = models.EmailField(max_length = 200)
    access_role = models.CharField(max_length=20, choices = ROLE_CHOICES, default = "Member")
    # deleted field
    isdeleted = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return str(self.id)

class Cwf(models.Model):
    #cwf_id = models.AutoField(primary_key=True)
    id = models.CharField(max_length = 100, primary_key=True)
    name = models.CharField(max_length = 255, blank = False, null = False)
    role = models.ManyToManyField("Role", related_name="cwf_role")
    creator = models.ForeignKey("User", on_delete = models.SET_NULL, null=True, related_name='cwf_creator')
    #assigned_to = models.ForeignKey("User", on_delete = models.SET_NULL, null=True, related_name='assigned_to')
    # deleted field
    isdeleted = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return self.id


class Kt(models.Model):
    #kt_id = models.AutoField(primary_key=True)
    id = models.CharField(max_length = 100, primary_key=True)
    name = models.CharField(max_length = 255, blank = False, null = False)
    role = models.ManyToManyField("Role")
    cwf = models.ManyToManyField("Cwf")
    creator = models.ForeignKey("User", on_delete = models.SET_NULL, null=True, related_name='kt_creator')
    # deleted field
    isdeleted = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return self.id

class Skill(models.Model):
    id = models.CharField(max_length = 100, primary_key=True)
    name = models.CharField(max_length = 255, blank = False, null = False)
    creator = models.ForeignKey("User", on_delete = models.SET_NULL, null=True, related_name='skill_creator')

    def __str__(self):
        return self.id

class SubSkill(models.Model):
    id = models.CharField(max_length = 100, primary_key=True)
    name = models.CharField(max_length = 255, blank = False, null = False)
    skill = models.ManyToManyField("Skill")
    creator = models.ForeignKey("User", on_delete = models.SET_NULL, null=True, related_name='subskill_creator')

    def __str__(self):
        return self.id

class Stage(models.Model):
    #stage_id = models.AutoField(primary_key=True)
    id = models.CharField(max_length = 100, primary_key=True)
    name = models.CharField(max_length = 255, blank = False, null = False)
    role = models.ManyToManyField("Role")
    order = models.IntegerField(default=0, blank=True)
    creator = models.ForeignKey("User", on_delete = models.SET_NULL, null=True, related_name='stage_creator')
    # deleted field
    isdeleted = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return self.id

class Qtype(models.Model):
    qtype_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length = 100, unique=True, blank = False, null = False)
    name = models.CharField(max_length = 255, blank = False, null = False)

    def __str__(self):
        return self.name

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    author = models.ForeignKey("User", on_delete = models.CASCADE, related_name="commentor")
    question = models.ForeignKey("Question", on_delete = models.CASCADE, related_name="commentor")
    content = models.TextField(max_length=500)
    date_posted = models.DateTimeField(auto_now_add=True, blank=True)
    last_updated_on = models.DateTimeField(auto_now=True, blank = True)
    mentioned = models.ManyToManyField("User", related_name='question_mentioned', blank=True)
    # deleted field
    isdeleted = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return self.content

class Snippet(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default='')
