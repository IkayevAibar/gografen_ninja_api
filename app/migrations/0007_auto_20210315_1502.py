# Generated by Django 3.1.7 on 2021-03-15 09:02

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_auto_20210315_1454'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lesson',
            name='teacher_id',
        ),
        migrations.AddField(
            model_name='lesson',
            name='teacher_id',
            field=models.ManyToManyField(blank=True, help_text='Учитель курса', null=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
