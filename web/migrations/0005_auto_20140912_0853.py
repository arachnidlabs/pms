# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0004_auto_20140906_0626'),
    ]

    operations = [
        migrations.AddField(
            model_name='tindieproduct',
            name='shipwire_warehouse',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='lineitem',
            name='package',
            field=models.ForeignKey(related_name=b'lineitems', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='web.Package', null=True),
        ),
    ]
