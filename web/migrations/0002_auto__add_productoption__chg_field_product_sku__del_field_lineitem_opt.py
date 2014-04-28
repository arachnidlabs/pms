# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ProductOption'
        db.create_table(u'web_productoption', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['web.Product'])),
            ('sku', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('shipping_weight', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('customs_value', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=8, decimal_places=2, blank=True)),
        ))
        db.send_create_signal(u'web', ['ProductOption'])


        # Changing field 'Product.sku'
        db.alter_column(u'web_product', 'sku', self.gf('django.db.models.fields.CharField')(max_length=32))
        # Deleting field 'LineItem.options'
        db.delete_column(u'web_lineitem', 'options')

        # Adding field 'LineItem.option_text'
        db.add_column(u'web_lineitem', 'option_text',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'ProductOption'
        db.delete_table(u'web_productoption')


        # Changing field 'Product.sku'
        db.alter_column(u'web_product', 'sku', self.gf('django.db.models.fields.CharField')(max_length=255))
        # Adding field 'LineItem.options'
        db.add_column(u'web_lineitem', 'options',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Deleting field 'LineItem.option_text'
        db.delete_column(u'web_lineitem', 'option_text')


    models = {
        u'web.lineitem': {
            'Meta': {'object_name': 'LineItem'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'option_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
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
            'sku': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        u'web.productoption': {
            'Meta': {'object_name': 'ProductOption'},
            'customs_value': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.Product']"}),
            'shipping_weight': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'sku': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        u'web.shippingmethod': {
            'Meta': {'object_name': 'ShippingMethod'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['web']