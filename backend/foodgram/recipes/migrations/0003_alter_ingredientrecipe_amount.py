# Generated by Django 4.2.5 on 2023-09-17 14:00

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientrecipe',
            name='amount',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Минимальное количество 1!'), django.core.validators.MaxValueValidator(2000, message='Максимальное количество!')], verbose_name='Количество'),
        ),
    ]
