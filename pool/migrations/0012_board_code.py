# Generated by Django 3.2.9 on 2021-12-09 20:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pool', '0011_alter_money_board_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='board',
            name='code',
            field=models.IntegerField(default=0),
        ),
    ]
