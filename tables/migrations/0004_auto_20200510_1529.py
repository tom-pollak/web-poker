# Generated by Django 3.0.3 on 2020-05-10 15:29

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tables', '0003_auto_20190804_1453'),
    ]

    operations = [
        migrations.AlterField(
            model_name='table',
            name='lastUsed',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]