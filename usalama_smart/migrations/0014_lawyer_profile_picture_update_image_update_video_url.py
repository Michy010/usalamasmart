# Generated by Django 4.2.6 on 2024-07-15 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usalama_smart', '0013_alter_content_content_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='lawyer',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='lawyer_profiles/'),
        ),
        migrations.AddField(
            model_name='update',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='updates/images/'),
        ),
        migrations.AddField(
            model_name='update',
            name='video_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
