# Generated by Django 4.2.6 on 2023-10-19 08:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentification', '0005_alter_workerdetails_location'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='services',
            name='locations',
        ),
        migrations.CreateModel(
            name='ServiceLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('locations', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentification.locations')),
                ('services', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentification.services')),
            ],
        ),
    ]
