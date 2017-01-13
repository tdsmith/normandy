# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2016-11-28 16:14
# flake8: noqa
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0035_revision_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='action',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='arguments_json',
        ),
        migrations.AlterField(
            model_name='recipe',
            name='filter_expression',
            field=models.TextField(blank=False, default=''),
            preserve_default=True,
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='filter_expression',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='last_updated',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='name',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='revision_id',
        ),
        migrations.AlterField(
            model_name='recipe',
            name='signature',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='recipe_revision', to='recipes.Signature'),
        ),
    ]
