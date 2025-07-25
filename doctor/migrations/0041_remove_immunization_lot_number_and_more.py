# Generated by Django 4.0.10 on 2023-06-28 14:44

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctor', '0040_alter_doctorrecordrequest_request_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='immunization',
            name='lot_number',
        ),
        migrations.RemoveField(
            model_name='vaccination',
            name='expiry_date',
        ),
        migrations.AddField(
            model_name='immunization',
            name='barangay_num',
            field=models.IntegerField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='immunization',
            name='birth_height',
            field=models.IntegerField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='immunization',
            name='birth_weight',
            field=models.IntegerField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='immunization',
            name='fam_num',
            field=models.IntegerField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='immunization',
            name='father_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='immunization',
            name='hfacility_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='immunization',
            name='mother_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='immunization',
            name='other_vaccine',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='immunization',
            name='place_birth',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='doctorrecordrequest',
            name='request_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 28, 22, 43, 19, 606343)),
        ),
        migrations.AlterField(
            model_name='immunization',
            name='dose_number',
            field=models.IntegerField(choices=[(1, 'At Birth'), (2, '1st Visit'), (3, '2nd Visit'), (4, '3rd Visit'), (5, '4th Visit'), (6, '5th Visit'), (7, 'Others')]),
        ),
        migrations.AlterField(
            model_name='immunization',
            name='immune_name',
            field=models.CharField(choices=[('BCG', 'BCG'), ('HEPATITIS B', 'HEPATITIS B'), ('PENTAVALENT VACCINE', 'PENTAVALENT VACCINE'), ('ORAL POLIO VACCINE', 'ORAL POLIO VACCINE'), ('INACTIVATED POLIO VACCINE', 'INACTIVATED POLIO VACCINE'), ('PNEUMOCOCCAL CONJUGATE VACCINE', 'PNEUMOCOCCAL CONJUGATE VACCINE'), ('MEASLES, MUMPS, RUBELLA', 'MEASLES, MUMPS, RUBELLA'), ('Others', 'Others')], max_length=200),
        ),
    ]
