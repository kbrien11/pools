# Generated by Django 3.2.9 on 2022-01-12 21:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pool', '0028_board_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeneratedNumbers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('winning', models.TextField(default='')),
                ('losing', models.TextField(default='')),
                ('board_pk', models.CharField(default='', max_length=20)),
            ],
        ),
    ]
