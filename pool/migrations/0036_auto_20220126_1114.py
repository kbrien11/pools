# Generated by Django 3.2.9 on 2022-01-26 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pool', '0035_auto_20220124_1741'),
    ]

    operations = [
        migrations.AddField(
            model_name='marchmadness',
            name='box_price',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='nfl',
            name='box_price',
            field=models.FloatField(default=0),
        ),
    ]