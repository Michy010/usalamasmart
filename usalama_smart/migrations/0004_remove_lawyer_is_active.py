# Generated by Django 4.2.6 on 2024-12-20 23:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usalama_smart', '0003_expert_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lawyer',
            name='is_active',
        ),
    ]