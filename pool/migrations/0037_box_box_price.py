# Generated by Django 3.2.9 on 2022-01-28 20:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pool', '0036_auto_20220126_1114'),
    ]

    operations = [
        migrations.AddField(
            model_name='box',
            name='box_price',
            field=models.FloatField(default=0),
        ),
    ]
