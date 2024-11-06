# Generated by Django 5.1.2 on 2024-11-04 20:44

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0011_publication_est_approuve'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Auteur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_inscription', models.DateField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Projet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titre', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('date_publication', models.DateTimeField(auto_now_add=True)),
                ('approuve', models.BooleanField(default=False)),
                ('auteur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projets', to='forum.auteur')),
            ],
        ),
    ]
