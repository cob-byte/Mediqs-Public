# Generated by Django 4.0.10 on 2023-05-20 09:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('healthcenter', '0003_medicalrecordrequest'),
        ('doctor', '0004_remove_medicalrecord_appointment_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicalrecord',
            name='request',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='healthcenter.medicalrecordrequest'),
        ),
    ]
