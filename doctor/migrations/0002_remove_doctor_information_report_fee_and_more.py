# Generated by Django 4.0.10 on 2023-05-19 06:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctor', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='doctor_information',
            name='report_fee',
        ),
        migrations.AlterField(
            model_name='doctor_information',
            name='dob',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='doctor_information',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
