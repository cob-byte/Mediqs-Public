# Generated by Django 4.0.10 on 2023-07-23 03:03

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('doctor', '0059_alter_doctorrecordrequest_request_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctorrecordrequest',
            name='request_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 7, 23, 3, 3, 18, 329885, tzinfo=utc)),
        ),
    ]
