# Generated by Django 3.2.9 on 2021-12-22 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pool', '0020_box_hit'),
    ]

    operations = [
        migrations.AddField(
            model_name='box',
            name='count',
            field=models.IntegerField(default=0),
        ),
    ]
