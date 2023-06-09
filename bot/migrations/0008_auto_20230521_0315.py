# Generated by Django 3.2.19 on 2023-05-21 00:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0007_auto_20230521_0310'),
    ]

    operations = [
        migrations.RenameField(
            model_name='student',
            old_name='name',
            new_name='telegram_name',
        ),
        migrations.AddField(
            model_name='request',
            name='more_contacts',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='request',
            name='student_course',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='request',
            name='student_name',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='student',
            name='telegram_username',
            field=models.TextField(default=''),
        ),
    ]
