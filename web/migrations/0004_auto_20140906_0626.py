# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0003_auto_20140906_0622'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='preorder',
            new_name='backorder',
        ),
    ]
