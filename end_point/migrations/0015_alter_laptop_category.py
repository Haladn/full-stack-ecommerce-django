# Generated by Django 4.1.9 on 2023-09-23 18:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('end_point', '0014_alter_laptop_color_alter_laptop_cpu_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='laptop',
            name='category',
            field=models.CharField(default='Gaming Laptop', max_length=100),
        ),
    ]
