# Generated by Django 4.2.6 on 2025-05-11 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usalama_smart', '0009_remove_content_company_incident_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='incident',
            name='located',
            field=models.CharField(default='Not Provided', max_length=255),
        ),
    ]
