# Generated by Django 3.2.19 on 2023-05-21 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0009_request_reason'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='request',
            name='more_contacts',
        ),
        migrations.RemoveField(
            model_name='request',
            name='student_course',
        ),
        migrations.RemoveField(
            model_name='request',
            name='student_name',
        ),
        migrations.AddField(
            model_name='request',
            name='ready',
            field=models.BooleanField(default=False),
        ),
    ]
