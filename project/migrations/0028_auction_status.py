# Generated by Django 3.0.4 on 2020-04-03 20:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0027_auto_20200327_2140'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='Status',
            field=models.CharField(default='Not started', max_length=100),
        ),
    ]
