# Generated by Django 4.2.6 on 2023-11-05 06:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentification', '0012_bookings_is_rejected'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookings',
            name='date',
            field=models.DateField(),
        ),
    ]