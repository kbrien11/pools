# Generated by Django 3.2.9 on 2022-03-07 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pool', '0041_marchmadnessdates'),
    ]

    operations = [
        migrations.AddField(
            model_name='marchmadnessdates',
            name='visited',
            field=models.BooleanField(default=False),
        ),
    ]