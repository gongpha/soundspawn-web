# Generated by Django 5.1.2 on 2024-11-03 19:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spa', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='picture',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='spa.upload'),
        ),
        migrations.AddField(
            model_name='playlist',
            name='picture',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='spa.upload'),
        ),
    ]
