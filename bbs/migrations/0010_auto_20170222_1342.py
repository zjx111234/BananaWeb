# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-22 13:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bbs', '0009_userprofile_user_real_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='article_like',
            field=models.ManyToManyField(blank=True, to='bbs.Article'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='mobile_phone',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]