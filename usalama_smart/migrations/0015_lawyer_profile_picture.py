# Generated by Django 4.2.6 on 2024-07-14 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usalama_smart', '0014_update_image_update_video_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='lawyer',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='lawyer_profiles/'),
        ),
    ]
