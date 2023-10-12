# Generated by Django 4.2.2 on 2023-10-01 16:13

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('mailing', '0002_alter_mailing_start_datetime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mailing',
            name='end_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='mailing',
            name='start_datetime',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
