# Generated by Django 2.2 on 2020-02-16 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0010_image_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='Image',
            field=models.ImageField(upload_to='static/images'),
        ),
    ]