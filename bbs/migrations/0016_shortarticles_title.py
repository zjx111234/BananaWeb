# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-27 17:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bbs', '0015_shortarticles'),
    ]

    operations = [
        migrations.AddField(
            model_name='shortarticles',
            name='title',
            field=models.CharField(default='无题', max_length=255, verbose_name='标题'),
        ),
    ]