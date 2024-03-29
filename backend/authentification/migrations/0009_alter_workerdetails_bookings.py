# Generated by Django 4.2.6 on 2023-10-31 14:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentification', '0008_workerdetails_join_date_bookings_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workerdetails',
            name='bookings',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='worker_bookings', to='authentification.bookings'),
        ),
    ]
