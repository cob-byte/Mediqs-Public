# Generated by Django 4.0.10 on 2023-06-28 14:44

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctor', '0041_remove_immunization_lot_number_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctorrecordrequest',
            name='request_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 28, 22, 44, 35, 724996)),
        ),
    ]
