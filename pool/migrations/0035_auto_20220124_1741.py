# Generated by Django 3.2.9 on 2022-01-24 22:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pool', '0034_auto_20220124_1735'),
    ]

    operations = [
        migrations.AlterField(
            model_name='marchmadness',
            name='board_number',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pool.board'),
        ),
        migrations.AlterField(
            model_name='nfl',
            name='board_number',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pool.board'),
        ),
    ]