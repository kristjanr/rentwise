# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-12 10:24
from __future__ import unicode_literals

from decimal import Decimal

import django.core.validators
from django.db import migrations, models

import app.fields
from app.models import Category

categories = [
    'Entertainment',
    'Technology',
    'Home Equipment',
    'Outdoors & Sports',
    'Machinery & Transport',
    'Luxury Goods & Clothing',
    'Office & Business',
]


def insert_categories(apps, schema_editor):
    for cat_name, cat in zip(categories, Category.objects.all()):
        cat.name = cat_name
        cat.save()


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0008_auto_20170111_1622'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.RunPython(insert_categories),
        migrations.AlterField(
            model_name='item',
            name='location',
            field=app.fields.LocationField(),
        ),
        migrations.AlterField(
            model_name='item',
            name='price_per_day',
            field=models.DecimalField(decimal_places=2, max_digits=6,
                                      validators=[django.core.validators.MaxValueValidator(5000),
                                                  django.core.validators.MinValueValidator(Decimal('0.01'))],
                                      verbose_name='price £/day'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='location',
            field=app.fields.LocationField(null=True),
        ),
    ]
