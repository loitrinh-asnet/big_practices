# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_auto_20160407_0127'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='blog',
            managers=[
            ],
        ),
        migrations.AlterModelManagers(
            name='comment',
            managers=[
            ],
        ),
        migrations.AlterModelManagers(
            name='entry',
            managers=[
            ],
        ),
    ]
