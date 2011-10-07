# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Domain'
        db.create_table('petition_domain', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('petition', ['Domain'])

        # Adding M2M table for field valid_domains on 'Campaign'
        db.create_table('petition_campaign_valid_domains', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('campaign', models.ForeignKey(orm['petition.campaign'], null=False)),
            ('domain', models.ForeignKey(orm['petition.domain'], null=False))
        ))
        db.create_unique('petition_campaign_valid_domains', ['campaign_id', 'domain_id'])


    def backwards(self, orm):
        
        # Deleting model 'Domain'
        db.delete_table('petition_domain')

        # Removing M2M table for field valid_domains on 'Campaign'
        db.delete_table('petition_campaign_valid_domains')


    models = {
        'petition.campaign': {
            'Meta': {'object_name': 'Campaign'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'valid_domains': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['petition.Domain']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'petition.domain': {
            'Meta': {'object_name': 'Domain'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'petition.signature': {
            'Meta': {'ordering': "['-is_verified', '-signed_date']", 'object_name': 'Signature'},
            'campaign': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['petition.Campaign']"}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'signed_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['petition']
