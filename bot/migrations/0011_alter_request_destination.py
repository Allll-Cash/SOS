# Generated by Django 3.2.19 on 2023-05-21 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0010_auto_20230521_2129'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='destination',
            field=models.TextField(db_index=True, null=True),
        ),
    ]
