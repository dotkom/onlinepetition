# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Campaign'
        db.create_table('petition_campaign', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('start_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('end_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('petition', ['Campaign'])

        # Adding model 'Signature'
        db.create_table('petition_signature', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('signed_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('campaign', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['petition.Campaign'])),
            ('is_verified', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('petition', ['Signature'])


    def backwards(self, orm):
        
        # Deleting model 'Campaign'
        db.delete_table('petition_campaign')

        # Deleting model 'Signature'
        db.delete_table('petition_signature')


    models = {
        'petition.campaign': {
            'Meta': {'object_name': 'Campaign'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
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
