# Generated by Django 3.1.7 on 2021-03-11 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20210311_1427'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=150, unique=True, verbose_name='email address'),
        ),
    ]
