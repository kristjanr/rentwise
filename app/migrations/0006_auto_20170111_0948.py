# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-11 09:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_item_created_at'),
    ]

    operations = [
        migrations.RenameField(
            model_name='item',
            old_name='published',
            new_name='is_published',
        ),
        migrations.AlterField(
            model_name='item',
            name='created_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Added on'),
        ),
    ]
