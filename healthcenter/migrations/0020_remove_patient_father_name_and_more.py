# Generated by Django 4.0.10 on 2023-06-20 05:18

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('healthcenter', '0019_alter_medicalrecordrequest_request_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='patient',
            name='father_name',
        ),
        migrations.AlterField(
            model_name='medicalrecordrequest',
            name='request_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 20, 13, 18, 18, 664233)),
        ),
    ]
