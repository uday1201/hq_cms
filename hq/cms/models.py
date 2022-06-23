from django.db import models
from django.core.validators import MinValueValidator
from datetime import datetime
from django.contrib.auth.models import AbstractUser

# Create your models here.
class Question(models.Model):
    STATUS_CHOICES = (
    ("SAVED", "Saved"),
    ("UNDERREVIEW", "Under Review"),
    ("REVIEWED", "Reviewed"),
    ("ARCHIVED", "Archived"),
    )
    qid = models.AutoField(primary_key=True)
    # details of the question
    cwf = models.ManyToManyField("Cwf",blank=True) # for ManyToManyField Django will automatically create a table to manage to manage many-to-many relationships
    kt = models.ManyToManyField("Kt",blank=True)
    role = models.ManyToManyField("Role",blank=True)
    stage = models.ForeignKey("Stage", on_delete = models.SET_NULL, null=True) # if the stage id is delelted it will set this field to NULL
    # assests for the question
    exhibits = models.ManyToManyField("Exhibit", blank=True)
    excels = models.ManyToManyField("Excel", blank=True)
    context = models.JSONField(blank=True, null=True)
    # content of the question
    text = models.CharField(max_length = 100, blank = False, null = False)
    qtype = models.ForeignKey("Qtype", on_delete = models.SET_NULL, null=True)
    options = models.JSONField(blank=True, null=True)
    score_type = models.CharField(max_length = 10, blank = False, null = False)
    score_weight = models.FloatField(validators = [MinValueValidator(0)])
    # extras
    resources = models.JSONField(blank=True, null=True)
    # timestamp and tracking
    creator = models.ForeignKey("User", on_delete = models.SET_NULL, null=True, related_name='question_creator') # if the creator user is deleted it will set this field to NULL
    approved_by = models.ForeignKey("User", on_delete = models.SET_NULL, null=True, related_name='question_approver') # if the user is deleted it will set this field to NULL
    last_edited_by = models.ForeignKey("User", on_delete = models.SET_NULL, null=True, related_name='question_editor') # if the user is deleted it will set this field to NULL
    last_edited = models.DateTimeField(default=datetime.now, blank = True)
    created = models.DateTimeField(auto_now_add=True, blank=True)
    # miscellaneous fields
    idealtime = models.FloatField(blank=True, null=True)
    difficulty_level = models.CharField(max_length=50, blank=True, null=True)
    misc = models.JSONField(blank=True, null=True)
    # status of the question
    status = models.CharField(max_length=20, choices = STATUS_CHOICES, default = "SAVED")

    def __str__(self):
        return str(self.qtype_id)

class Assessment(models.Model):
    aid = models.AutoField(primary_key=True)
    problem_statement = models.CharField(max_length=1000, blank = True)
    questions = models.ManyToManyField("Question",blank=True)
    role = models.ManyToManyField("Role",blank=True)
    remarks = models.CharField(max_length=1000, blank = True)
    # timestamp and tracking
    creator = models.ForeignKey("User", on_delete = models.SET_NULL, null=True, related_name='assessment_creator') # if the creator user is deleted it will set this field to NULL
    approved_by = models.ForeignKey("User", on_delete = models.SET_NULL, null=True, related_name='assessment_approver') # if the user is deleted it will set this field to NULL
    last_updated = models.DateTimeField(default=datetime.now, blank = True)
    created = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return str(self.aid)

class Role(models.Model):
    role_id = models.AutoField(primary_key=True)
    role_code = models.CharField(max_length = 20, blank = False, null = False, unique=True)
    role_name = models.CharField(max_length = 100, blank = False)

    def __str__(self):
        return self.role_name

class Exhibit(models.Model):
    exhibit_id = models.AutoField(primary_key=True)
    # we have 2 choices here, if we want to store the assests externally on the cloud we need to have a URL field, otherwise we can also use Django media manager with imagefield
    #url = models.URLField(max_length = 250)
    #file = models.FileField(upload_to = 'exhibits/')
    image = models.ImageField(upload_to = 'exhibits/', blank=True)
    alt_text = models.CharField(max_length = 100, blank = True)
    type = models.CharField(max_length = 100, blank = True)
    created_on = models.DateTimeField(default=datetime.now, blank = True)

    def __str__(self):
        return self.alt_text

class Excel(models.Model):
    excel_id = models.AutoField(primary_key=True)
    #url = models.URLField(max_length = 250)
    file = models.FileField(upload_to = 'exhibits/', blank=True)
    alt_text = models.CharField(max_length = 100, blank = True)
    created_on = models.DateTimeField(default=datetime.now, blank = True)

    def __str__(self):
        return self.alt_text


# for the users we can also use the Django's inbuilt user management system
# we will use the inbuilt one
class User(AbstractUser):
    email = models.EmailField(max_length = 200)
    access_role = models.CharField(max_length = 100)

    def __str__(self):
        return self.first_name

class Cwf(models.Model):
    cwf_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length = 100, unique=True, blank = False, null = False)
    name = models.CharField(max_length = 255, blank = False, null = False)
    role = models.ManyToManyField("Role")
    #assigned_to = models.ForeignKey("User", on_delete = models.SET_NULL, null=True, related_name='assigned_to')

    def __str__(self):
        return self.name


class Kt(models.Model):
    kt_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length = 100, unique=True, blank = False, null = False)
    name = models.CharField(max_length = 255, blank = False, null = False)
    role = models.ManyToManyField("Role")
    cwf = models.ManyToManyField("Cwf")

    def __str__(self):
        return self.name

class Stage(models.Model):
    stage_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length = 100, unique=True, blank = False, null = False)
    name = models.CharField(max_length = 255, blank = False, null = False)
    role = models.ManyToManyField("Role")
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Qtype(models.Model):
    qtype_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length = 100, unique=True, blank = False, null = False)
    name = models.CharField(max_length = 255, blank = False, null = False)

    def __str__(self):
        return self.name

class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    author = models.ForeignKey("User", on_delete = models.CASCADE, related_name="commentor")
    question = models.ForeignKey("Question", on_delete = models.CASCADE, related_name="commentor")
    content = models.TextField(max_length=500)
    date_posted = models.DateTimeField(auto_now_add=True, blank=True)
    last_updated_on = models.DateTimeField(auto_now=True, blank = True)
    mentioned = models.ManyToManyField("User", related_name='question_mentioned', blank=True)

    def __str__(self):
        return self.content
