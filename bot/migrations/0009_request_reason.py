# Generated by Django 3.2.19 on 2023-05-21 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0008_auto_20230521_0315'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='reason',
            field=models.TextField(default=''),
        ),
    ]
