# Generated by Django 2.2.1 on 2019-10-02 14:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('poker', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='players',
            name='poker',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='poker.Room'),
        ),
    ]
