# Generated by Django 4.0.10 on 2023-07-30 07:34

from django.db import migrations, models
import doctor.models


class Migration(migrations.Migration):

    dependencies = [
        ('doctor', '0061_alter_doctorrecordrequest_request_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicalrecord',
            name='serial_number',
            field=models.CharField(default=doctor.models.generate_random_string, max_length=8),
        ),
        migrations.AddField(
            model_name='prescription',
            name='serial_number',
            field=models.CharField(default=doctor.models.generate_random_string, max_length=8),
        ),
    ]
