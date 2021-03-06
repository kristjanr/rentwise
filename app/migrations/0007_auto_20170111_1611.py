# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-11 16:11
from __future__ import unicode_literals

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_auto_20170111_0948'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='description',
            field=models.TextField(max_length=5000, validators=[django.core.validators.MinLengthValidator(20)]),
        ),
        migrations.AlterField(
            model_name='item',
            name='estimated_value',
            field=models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='value £'),
        ),
        migrations.AlterField(
            model_name='item',
            name='minimum_rental_period',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(500)], verbose_name='min. days'),
        ),
        migrations.AlterField(
            model_name='item',
            name='name',
            field=models.TextField(max_length=100, validators=[django.core.validators.MinLengthValidator(5)]),
        ),
        migrations.AlterField(
            model_name='item',
            name='price_per_day',
            field=models.DecimalField(decimal_places=2, max_digits=6, validators=[django.core.validators.MinValueValidator(Decimal('0.01')), django.core.validators.MaxValueValidator(5000)], verbose_name='price £/day'),
        ),
    ]
