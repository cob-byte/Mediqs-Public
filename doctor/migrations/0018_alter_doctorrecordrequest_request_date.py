# Generated by Django 4.0.10 on 2023-06-20 18:56
# Generated by Django 4.0.10 on 2023-06-20 03:05

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctor', '0017_appointment_urgency_and_more'),
        ('doctor', '0017_alter_doctorrecordrequest_request_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctorrecordrequest',
            name='request_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 21, 2, 56, 21, 607637)),
        ),
    ]
