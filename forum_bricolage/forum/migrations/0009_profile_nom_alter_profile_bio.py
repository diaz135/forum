# Generated by Django 5.1.2 on 2024-11-03 22:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0008_remove_profile_profile_picture_alter_profile_bio'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='nom',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='profile',
            name='bio',
            field=models.TextField(blank=True),
        ),
    ]
