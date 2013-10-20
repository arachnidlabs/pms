# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ShippingMethod'
        db.create_table(u'web_shippingmethod', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'web', ['ShippingMethod'])

        # Adding model 'Order'
        db.create_table(u'web_order', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('remote_order_id', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('message', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('payment', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('refunded', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('shipped', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('shipping_city', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('shipping_country', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('shipping_instructions', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('shipping_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('shipping_postcode', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('shipping_method', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['web.ShippingMethod'])),
            ('shipping_state', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('shipping_street', self.gf('django.db.models.fields.TextField')()),
            ('total', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2)),
            ('total_discount', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2)),
            ('total_kickback', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2)),
            ('total_seller', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2)),
            ('total_shipping', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2)),
            ('total_subtotal', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2)),
            ('total_tindiefee', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2)),
            ('tracking_code', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('tracking_url', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal(u'web', ['Order'])

        # Adding model 'Product'
        db.create_table(u'web_product', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sku', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('shipping_weight', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('customs_value', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=8, decimal_places=2, blank=True)),
        ))
        db.send_create_signal(u'web', ['Product'])

        # Adding model 'LineItem'
        db.create_table(u'web_lineitem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['web.Order'])),
            ('package', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['web.Package'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['web.Product'])),
            ('options', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('pre_order', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('price_total', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2)),
            ('price_unit', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2)),
            ('quantity', self.gf('django.db.models.fields.IntegerField')()),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'web', ['LineItem'])

        # Adding model 'Package'
        db.create_table(u'web_package', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['web.Order'])),
            ('posting', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['web.Posting'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('shipping_method', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['web.ShippingMethod'])),
            ('shipping_weight', self.gf('django.db.models.fields.IntegerField')()),
            ('customs_value', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2)),
            ('packed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('sent', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'web', ['Package'])

        # Adding model 'Posting'
        db.create_table(u'web_posting', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipping_method', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['web.ShippingMethod'])),
            ('provider_id', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal(u'web', ['Posting'])


    def backwards(self, orm):
        # Deleting model 'ShippingMethod'
        db.delete_table(u'web_shippingmethod')

        # Deleting model 'Order'
        db.delete_table(u'web_order')

        # Deleting model 'Product'
        db.delete_table(u'web_product')

        # Deleting model 'LineItem'
        db.delete_table(u'web_lineitem')

        # Deleting model 'Package'
        db.delete_table(u'web_package')

        # Deleting model 'Posting'
        db.delete_table(u'web_posting')


    models = {
        u'web.lineitem': {
            'Meta': {'object_name': 'LineItem'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'options': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.Order']"}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.Package']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'pre_order': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'price_total': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'price_unit': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.Product']"}),
            'quantity': ('django.db.models.fields.IntegerField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'web.order': {
            'Meta': {'object_name': 'Order'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'payment': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'refunded': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'remote_order_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'shipped': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'shipping_city': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'shipping_country': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'shipping_instructions': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'shipping_method': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.ShippingMethod']"}),
            'shipping_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'shipping_postcode': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'shipping_state': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'shipping_street': ('django.db.models.fields.TextField', [], {}),
            'total': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'total_discount': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'total_kickback': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'total_seller': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'total_shipping': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'total_subtotal': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'total_tindiefee': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'tracking_code': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'tracking_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'web.package': {
            'Meta': {'object_name': 'Package'},
            'customs_value': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.Order']"}),
            'packed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'posting': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.Posting']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'shipping_method': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.ShippingMethod']"}),
            'shipping_weight': ('django.db.models.fields.IntegerField', [], {})
        },
        u'web.posting': {
            'Meta': {'object_name': 'Posting'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'provider_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'shipping_method': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.ShippingMethod']"})
        },
        u'web.product': {
            'Meta': {'object_name': 'Product'},
            'customs_value': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'shipping_weight': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'sku': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'web.shippingmethod': {
            'Meta': {'object_name': 'ShippingMethod'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['web']