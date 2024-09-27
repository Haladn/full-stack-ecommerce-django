# Generated by Django 4.1.9 on 2023-09-07 02:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('end_point', '0007_alter_laptop_color_alter_laptop_cpu_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='laptop',
            name='brand',
        ),
        migrations.AlterField(
            model_name='laptop',
            name='category',
            field=models.CharField(choices=[('Gaming Laptops', 'Gaming Laptops')], default='electronics', max_length=100),
        ),
    ]
