# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-02-18 11:02
from __future__ import unicode_literals

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_address'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='address',
            managers=[
                ('object', django.db.models.manager.Manager()),
            ],
        ),
    ]
