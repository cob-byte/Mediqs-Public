# Generated by Django 4.0.10 on 2023-06-24 10:05

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctor', '0027_remove_immunization_barangay_num_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor_review',
            name='symptoms',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='doctorrecordrequest',
            name='request_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 24, 18, 5, 18, 129642)),
        ),
    ]
