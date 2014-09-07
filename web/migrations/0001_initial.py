# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LineItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('options', models.TextField(null=True, blank=True)),
                ('pre_order', models.BooleanField(default=False)),
                ('price_total', models.DecimalField(max_digits=8, decimal_places=2)),
                ('price_unit', models.DecimalField(max_digits=8, decimal_places=2)),
                ('quantity', models.IntegerField()),
                ('status', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('remote_order_id', models.CharField(max_length=255, null=True, blank=True)),
                ('date', models.DateTimeField()),
                ('email', models.CharField(max_length=255)),
                ('message', models.TextField(null=True, blank=True)),
                ('payment', models.CharField(max_length=255, null=True, blank=True)),
                ('phone', models.CharField(max_length=255, null=True, blank=True)),
                ('refunded', models.BooleanField(default=False)),
                ('shipped', models.BooleanField(default=False)),
                ('shipping_city', models.CharField(max_length=255)),
                ('shipping_country', models.CharField(max_length=255)),
                ('shipping_instructions', models.TextField(null=True, blank=True)),
                ('shipping_name', models.CharField(max_length=255)),
                ('shipping_postcode', models.CharField(max_length=255)),
                ('shipping_state', models.CharField(max_length=255, blank=True)),
                ('shipping_street', models.TextField()),
                ('total', models.DecimalField(max_digits=8, decimal_places=2)),
                ('total_discount', models.DecimalField(max_digits=8, decimal_places=2)),
                ('total_kickback', models.DecimalField(max_digits=8, decimal_places=2)),
                ('total_seller', models.DecimalField(max_digits=8, decimal_places=2)),
                ('total_shipping', models.DecimalField(max_digits=8, decimal_places=2)),
                ('total_subtotal', models.DecimalField(max_digits=8, decimal_places=2)),
                ('total_tindiefee', models.DecimalField(max_digits=8, decimal_places=2)),
                ('tracking_code', models.CharField(max_length=255, null=True, blank=True)),
                ('tracking_url', models.CharField(max_length=255, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('shipping_weight', models.IntegerField()),
                ('customs_value', models.DecimalField(max_digits=8, decimal_places=2)),
                ('packed', models.BooleanField(default=False)),
                ('sent', models.BooleanField(default=False)),
                ('order', models.ForeignKey(to='web.Order')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Posting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('provider_id', models.CharField(max_length=255, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sku', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('shipping_weight', models.IntegerField(null=True, blank=True)),
                ('customs_value', models.DecimalField(null=True, max_digits=8, decimal_places=2, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ShippingMethod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('region', models.CharField(max_length=255, null=True, blank=True)),
                ('service_level', models.CharField(max_length=8, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TindieProduct',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tindie_id', models.IntegerField()),
                ('model_number', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('shipwire_rates', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TindieProductMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.IntegerField()),
                ('product', models.ForeignKey(related_name=b'tindie_products', to='web.Product')),
                ('tindie_product', models.ForeignKey(related_name=b'skus', to='web.TindieProduct')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='posting',
            name='shipping_method',
            field=models.ForeignKey(to='web.ShippingMethod'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='package',
            name='posting',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='web.Posting', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='package',
            name='shipping_method',
            field=models.ForeignKey(to='web.ShippingMethod'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_method',
            field=models.ForeignKey(to='web.ShippingMethod'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='lineitem',
            name='order',
            field=models.ForeignKey(to='web.Order'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='lineitem',
            name='package',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='web.Package', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='lineitem',
            name='product',
            field=models.ForeignKey(to='web.Product'),
            preserve_default=True,
        ),
    ]
