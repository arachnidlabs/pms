# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_auto_20140906_0542'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='preorder',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='lineitem',
            name='order',
            field=models.ForeignKey(related_name=b'lineitems', to='web.Order'),
        ),
    ]
