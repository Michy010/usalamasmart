# Generated by Django 4.2.6 on 2024-12-15 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usalama_smart', '0002_alter_lawyer_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='expert',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]
