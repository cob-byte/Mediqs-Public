# Generated by Django 4.0.10 on 2023-06-22 02:05

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctor', '0025_alter_doctorrecordrequest_request_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctorrecordrequest',
            name='request_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 22, 10, 5, 44, 544961)),
        ),
    ]
