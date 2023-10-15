# Generated by Django 4.2.6 on 2023-10-14 06:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentification', '0002_workerdetails_customuser_is_approved_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_profile_created',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='workerdetails',
            name='phone',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
