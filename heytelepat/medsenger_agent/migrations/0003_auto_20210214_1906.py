# Generated by Django 3.1.5 on 2021-02-14 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medsenger_agent', '0002_auto_20210214_1906'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='show',
            field=models.BooleanField(default=None),
        ),
    ]
