# Generated by Django 4.1.9 on 2023-12-15 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('end_point', '0018_alter_laptop_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='laptop',
            name='image',
            field=models.ImageField(max_length=500, null=True, upload_to=''),
        ),
    ]
