# Generated by Django 3.2.19 on 2023-05-21 00:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0006_alter_student_entered_faculty'),
    ]

    operations = [
        migrations.RenameField(
            model_name='student',
            old_name='telegram_name',
            new_name='name',
        ),
        migrations.RemoveField(
            model_name='student',
            name='telegram_username',
        ),
    ]
