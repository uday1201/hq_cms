# Generated by Django 4.0.5 on 2022-06-09 02:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0003_alter_question_context_alter_question_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='context',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
