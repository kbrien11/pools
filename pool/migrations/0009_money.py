# Generated by Django 3.2.9 on 2021-12-09 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pool', '0008_alter_box_user_pk'),
    ]

    operations = [
        migrations.CreateModel(
            name='Money',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first', models.FloatField()),
                ('second', models.FloatField()),
                ('third', models.FloatField()),
                ('fourth', models.FloatField()),
            ],
        ),
    ]
