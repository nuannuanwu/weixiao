# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Teacher'
        db.create_table('kinger_teacher', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('is_delete', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ctime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['auth.User'])),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('school', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kinger.School'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('appellation', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=765, blank=True)),
        ))
        db.send_create_signal('kinger', ['Teacher'])

        # Adding model 'Group'
        db.create_table('kinger_group', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('is_delete', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ctime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('school', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kinger.School'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('logo', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('year', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('sn', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('announcement', self.gf('django.db.models.fields.CharField')(max_length=765, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=765, blank=True)),
        ))
        db.send_create_signal('kinger', ['Group'])

        # Adding M2M table for field teachers on 'Group'
        db.create_table('kinger_group_teachers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('group', models.ForeignKey(orm['kinger.group'], null=False)),
            ('teacher', models.ForeignKey(orm['kinger.teacher'], null=False))
        ))
        db.create_unique('kinger_group_teachers', ['group_id', 'teacher_id'])

        # Adding model 'School'
        db.create_table('kinger_school', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('is_delete', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ctime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('area', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('province', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('sys', self.gf('django.db.models.fields.CharField')(max_length=9, null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=765, blank=True)),
        ))
        db.send_create_signal('kinger', ['School'])

        # Adding M2M table for field admins on 'School'
        db.create_table('kinger_school_admins', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('school', models.ForeignKey(orm['kinger.school'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('kinger_school_admins', ['school_id', 'user_id'])

        # Adding model 'Sms'
        db.create_table('kinger_sms', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('is_delete', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ctime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('sender', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sender', null=True, to=orm['auth.User'])),
            ('receiver', self.gf('django.db.models.fields.related.ForeignKey')(related_name='receiver', to=orm['auth.User'])),
            ('mobile', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('send_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('is_send', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('type', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('content', self.gf('django.db.models.fields.CharField')(max_length=765, blank=True)),
        ))
        db.send_create_signal('kinger', ['Sms'])

        # Adding model 'Student'
        db.create_table('kinger_student', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('is_delete', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ctime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['auth.User'])),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('school', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kinger.School'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='students', null=True, to=orm['kinger.Group'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=90)),
            ('gender', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('birth_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('sn', self.gf('django.db.models.fields.CharField')(max_length=36, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=765, blank=True)),
        ))
        db.send_create_signal('kinger', ['Student'])

        # Adding model 'TileTag'
        db.create_table('kinger_tiletag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_delete', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ctime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=120, unique=True, null=True)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=765, blank=True)),
        ))
        db.send_create_signal('kinger', ['TileTag'])

        # Adding model 'TileType'
        db.create_table('kinger_tile_type', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_delete', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ctime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=765, blank=True)),
            ('img', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('kinger', ['TileType'])

        # Adding model 'TileCategory'
        db.create_table('kinger_tile_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_delete', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ctime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=765, blank=True)),
            ('img', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kinger.TileCategory'], null=True, blank=True)),
            ('is_tips', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('sort', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('kinger', ['TileCategory'])

        # Adding model 'Tile'
        db.create_table('kinger_tile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_delete', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ctime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['auth.User'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='tiles', null=True, to=orm['auth.User'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kinger.Group'], null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kinger.TileType'])),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['kinger.TileCategory'], null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('img', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('n_comments', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('n_likers', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_tips', self.gf('django.db.models.fields.IntegerField')(default=0, null=True)),
            ('video', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=765, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')(max_length=765, blank=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('rating_votes', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, blank=True)),
            ('rating_score', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
        ))
        db.send_create_signal('kinger', ['Tile'])

        # Adding M2M table for field tags on 'Tile'
        db.create_table('kinger_tile_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('tile', models.ForeignKey(orm['kinger.tile'], null=False)),
            ('tiletag', models.ForeignKey(orm['kinger.tiletag'], null=False))
        ))
        db.create_unique('kinger_tile_tags', ['tile_id', 'tiletag_id'])

        # Adding model 'EventType'
        db.create_table('kinger_eventtype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_delete', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ctime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('img', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('group', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('kinger', ['EventType'])

        # Adding model 'EventSetting'
        db.create_table('kinger_eventsetting', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_delete', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ctime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='settings', to=orm['kinger.EventType'])),
            ('content', self.gf('django.db.models.fields.TextField')(max_length=765)),
            ('school', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kinger.School'], null=True, blank=True)),
        ))
        db.send_create_signal('kinger', ['EventSetting'])

        # Adding model 'CommentTemplaterType'
        db.create_table('kinger_comment_templatertype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_delete', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ctime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=765, blank=True)),
        ))
        db.send_create_signal('kinger', ['CommentTemplaterType'])

        # Adding model 'CommentTemplater'
        db.create_table('kinger_comment_templater', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_delete', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ctime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='templaters', to=orm['kinger.CommentTemplaterType'])),
            ('content', self.gf('django.db.models.fields.TextField')(max_length=765, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['auth.User'])),
        ))
        db.send_create_signal('kinger', ['CommentTemplater'])

        # Adding model 'Mentor'
        db.create_table('kinger_mentor', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('is_delete', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ctime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['auth.User'])),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(related_name='mentor', unique=True, to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('appellation', self.gf('django.db.models.fields.TextField')(max_length=60)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=765, blank=True)),
        ))
        db.send_create_signal('kinger', ['Mentor'])

        # Adding model 'Waiter'
        db.create_table('kinger_waiter', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('is_delete', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ctime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='waiter_creator', to=orm['auth.User'])),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(related_name='waiter', unique=True, to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('appellation', self.gf('django.db.models.fields.TextField')(max_length=60)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=765, blank=True)),
        ))
        db.send_create_signal('kinger', ['Waiter'])

        # Adding model 'Device'
        db.create_table('kinger_device', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ctime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='device', to=orm['auth.User'])),
            ('token', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
        ))
        db.send_create_signal('kinger', ['Device'])

        # Adding model 'ApplePushNotification'
        db.create_table('kinger_applepushnotification', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ctime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['auth.User'])),
            ('alert', self.gf('django.db.models.fields.TextField')()),
            ('badge', self.gf('django.db.models.fields.IntegerField')(default=1, max_length=30, null=True, blank=True)),
            ('sound', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('tile', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['kinger.Tile'], unique=True, null=True, blank=True)),
            ('is_send', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('send_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('kinger', ['ApplePushNotification'])

        # Adding model 'UserLastTile'
        db.create_table('kinger_userlasttile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(related_name='last_tile', unique=True, to=orm['auth.User'])),
            ('last_tile_id', self.gf('django.db.models.fields.IntegerField')(max_length=11, blank=True)),
        ))
        db.send_create_signal('kinger', ['UserLastTile'])

        # Adding model 'ChangeUsername'
        db.create_table('kinger_changeusername', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='user', to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('edittime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('kinger', ['ChangeUsername'])

        # Adding model 'Cookbook'
        db.create_table('kinger_cookbook', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ctime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('breakfast', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('light_breakfast', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('lunch', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('light_lunch', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('dinner', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('light_dinner', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('school', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kinger.School'], null=True, blank=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kinger.Group'], null=True, blank=True)),
        ))
        db.send_create_signal('kinger', ['Cookbook'])

        # Adding unique constraint on 'Cookbook', fields ['school', 'date']
        db.create_unique('kinger_cookbook', ['school_id', 'date'])

        # Adding unique constraint on 'Cookbook', fields ['group', 'date']
        db.create_unique('kinger_cookbook', ['group_id', 'date'])

        # Adding model 'CookbookSet'
        db.create_table('kinger_cookbookset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ctime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('school', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['kinger.School'], unique=True)),
            ('breakfast', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('light_breakfast', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('lunch', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('light_lunch', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('dinner', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('light_dinner', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('kinger', ['CookbookSet'])

        # Adding model 'VerifySms'
        db.create_table('kinger_verifysms', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('is_delete', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ctime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('sms', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['kinger.Sms'], unique=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('mobile', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('content', self.gf('django.db.models.fields.CharField')(max_length=765, blank=True)),
            ('vcode', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('kinger', ['VerifySms'])

        # Adding model 'MessageToClass'
        db.create_table('kinger_message_to_class', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_delete', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ctime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kinger.Group'], null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('content', self.gf('django.db.models.fields.CharField')(max_length=765, blank=True)),
        ))
        db.send_create_signal('kinger', ['MessageToClass'])

    def backwards(self, orm):
        # Removing unique constraint on 'Cookbook', fields ['group', 'date']
        db.delete_unique('kinger_cookbook', ['group_id', 'date'])

        # Removing unique constraint on 'Cookbook', fields ['school', 'date']
        db.delete_unique('kinger_cookbook', ['school_id', 'date'])

        # Deleting model 'Teacher'
        db.delete_table('kinger_teacher')

        # Deleting model 'Group'
        db.delete_table('kinger_group')

        # Removing M2M table for field teachers on 'Group'
        db.delete_table('kinger_group_teachers')

        # Deleting model 'School'
        db.delete_table('kinger_school')

        # Removing M2M table for field admins on 'School'
        db.delete_table('kinger_school_admins')

        # Deleting model 'Sms'
        db.delete_table('kinger_sms')

        # Deleting model 'Student'
        db.delete_table('kinger_student')

        # Deleting model 'TileTag'
        db.delete_table('kinger_tiletag')

        # Deleting model 'TileType'
        db.delete_table('kinger_tile_type')

        # Deleting model 'TileCategory'
        db.delete_table('kinger_tile_category')

        # Deleting model 'Tile'
        db.delete_table('kinger_tile')

        # Removing M2M table for field tags on 'Tile'
        db.delete_table('kinger_tile_tags')

        # Deleting model 'EventType'
        db.delete_table('kinger_eventtype')

        # Deleting model 'EventSetting'
        db.delete_table('kinger_eventsetting')

        # Deleting model 'CommentTemplaterType'
        db.delete_table('kinger_comment_templatertype')

        # Deleting model 'CommentTemplater'
        db.delete_table('kinger_comment_templater')

        # Deleting model 'Mentor'
        db.delete_table('kinger_mentor')

        # Deleting model 'Waiter'
        db.delete_table('kinger_waiter')

        # Deleting model 'Device'
        db.delete_table('kinger_device')

        # Deleting model 'ApplePushNotification'
        db.delete_table('kinger_applepushnotification')

        # Deleting model 'UserLastTile'
        db.delete_table('kinger_userlasttile')

        # Deleting model 'ChangeUsername'
        db.delete_table('kinger_changeusername')

        # Deleting model 'Cookbook'
        db.delete_table('kinger_cookbook')

        # Deleting model 'CookbookSet'
        db.delete_table('kinger_cookbookset')

        # Deleting model 'VerifySms'
        db.delete_table('kinger_verifysms')

        # Deleting model 'MessageToClass'
        db.delete_table('kinger_message_to_class')

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'kinger.applepushnotification': {
            'Meta': {'ordering': "['-ctime']", 'object_name': 'ApplePushNotification'},
            'alert': ('django.db.models.fields.TextField', [], {}),
            'badge': ('django.db.models.fields.IntegerField', [], {'default': '1', 'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['auth.User']"}),
            'ctime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_send': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'send_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'sound': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'tile': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['kinger.Tile']", 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'kinger.changeusername': {
            'Meta': {'ordering': "['-edittime']", 'object_name': 'ChangeUsername'},
            'edittime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user'", 'to': "orm['auth.User']"})
        },
        'kinger.commenttemplater': {
            'Meta': {'object_name': 'CommentTemplater', 'db_table': "'kinger_comment_templater'"},
            'content': ('django.db.models.fields.TextField', [], {'max_length': '765', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['auth.User']"}),
            'ctime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_delete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'templaters'", 'to': "orm['kinger.CommentTemplaterType']"})
        },
        'kinger.commenttemplatertype': {
            'Meta': {'object_name': 'CommentTemplaterType', 'db_table': "'kinger_comment_templatertype'"},
            'ctime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '765', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_delete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '120'})
        },
        'kinger.cookbook': {
            'Meta': {'unique_together': "(('school', 'date'), ('group', 'date'))", 'object_name': 'Cookbook'},
            'breakfast': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'ctime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'dinner': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kinger.Group']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'light_breakfast': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'light_dinner': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'light_lunch': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'lunch': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kinger.School']", 'null': 'True', 'blank': 'True'})
        },
        'kinger.cookbookset': {
            'Meta': {'object_name': 'CookbookSet'},
            'breakfast': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'ctime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'dinner': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'light_breakfast': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'light_dinner': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'light_lunch': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'lunch': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'school': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['kinger.School']", 'unique': 'True'})
        },
        'kinger.device': {
            'Meta': {'object_name': 'Device'},
            'ctime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'device'", 'to': "orm['auth.User']"})
        },
        'kinger.eventsetting': {
            'Meta': {'object_name': 'EventSetting'},
            'content': ('django.db.models.fields.TextField', [], {'max_length': '765'}),
            'ctime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_delete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kinger.School']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'settings'", 'to': "orm['kinger.EventType']"})
        },
        'kinger.eventtype': {
            'Meta': {'object_name': 'EventType'},
            'ctime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'is_delete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '120'})
        },
        'kinger.group': {
            'Meta': {'ordering': "['name']", 'object_name': 'Group'},
            'announcement': ('django.db.models.fields.CharField', [], {'max_length': '765', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'ctime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '765', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_delete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kinger.School']"}),
            'sn': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'teachers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'groups'", 'null': 'True', 'to': "orm['kinger.Teacher']"}),
            'year': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'})
        },
        'kinger.mentor': {
            'Meta': {'ordering': "['name']", 'object_name': 'Mentor'},
            'appellation': ('django.db.models.fields.TextField', [], {'max_length': '60'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['auth.User']"}),
            'ctime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '765', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_delete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'mentor'", 'unique': 'True', 'to': "orm['auth.User']"})
        },
        'kinger.messagetoclass': {
            'Meta': {'object_name': 'MessageToClass', 'db_table': "'kinger_message_to_class'"},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '765', 'blank': 'True'}),
            'ctime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kinger.Group']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_delete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'kinger.school': {
            'Meta': {'ordering': "['name']", 'object_name': 'School'},
            'admins': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'manageSchools'", 'null': 'True', 'to': "orm['auth.User']"}),
            'area': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'ctime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '765', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_delete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'province': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'sys': ('django.db.models.fields.CharField', [], {'max_length': '9', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'kinger.sms': {
            'Meta': {'ordering': "['-ctime']", 'object_name': 'Sms'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '765', 'blank': 'True'}),
            'ctime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_delete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_send': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mobile': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'receiver': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'receiver'", 'to': "orm['auth.User']"}),
            'send_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sender'", 'null': 'True', 'to': "orm['auth.User']"}),
            'type': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'kinger.student': {
            'Meta': {'ordering': "['name']", 'object_name': 'Student'},
            'birth_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['auth.User']"}),
            'ctime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '765', 'blank': 'True'}),
            'gender': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'students'", 'null': 'True', 'to': "orm['kinger.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_delete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '90'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kinger.School']"}),
            'sn': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'kinger.teacher': {
            'Meta': {'ordering': "['name']", 'object_name': 'Teacher'},
            'appellation': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['auth.User']"}),
            'ctime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '765', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_delete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kinger.School']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'kinger.tile': {
            'Meta': {'ordering': "['-start_time']", 'object_name': 'Tile'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'default': '0', 'to': "orm['kinger.TileCategory']", 'null': 'True', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {'max_length': '765', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['auth.User']"}),
            'ctime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '765', 'blank': 'True'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kinger.Group']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'is_delete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_tips': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'n_comments': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'n_likers': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'rating_score': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'rating_votes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'tiles'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['kinger.TileTag']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kinger.TileType']"}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'tiles'", 'null': 'True', 'to': "orm['auth.User']"}),
            'video': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'kinger.tilecategory': {
            'Meta': {'ordering': "('sort', 'id')", 'object_name': 'TileCategory', 'db_table': "'kinger_tile_category'"},
            'ctime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '765', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'is_delete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_tips': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kinger.TileCategory']", 'null': 'True', 'blank': 'True'}),
            'sort': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'kinger.tiletag': {
            'Meta': {'object_name': 'TileTag'},
            'ctime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '765', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_delete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '120', 'unique': 'True', 'null': 'True'})
        },
        'kinger.tiletype': {
            'Meta': {'ordering': "('id',)", 'object_name': 'TileType', 'db_table': "'kinger_tile_type'"},
            'ctime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '765', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'is_delete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '120'})
        },
        'kinger.userlasttile': {
            'Meta': {'object_name': 'UserLastTile'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_tile_id': ('django.db.models.fields.IntegerField', [], {'max_length': '11', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'last_tile'", 'unique': 'True', 'to': "orm['auth.User']"})
        },
        'kinger.verifysms': {
            'Meta': {'object_name': 'VerifySms'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '765', 'blank': 'True'}),
            'ctime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_delete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mobile': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'sms': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['kinger.Sms']", 'unique': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'vcode': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'kinger.waiter': {
            'Meta': {'ordering': "['name']", 'object_name': 'Waiter'},
            'appellation': ('django.db.models.fields.TextField', [], {'max_length': '60'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'waiter_creator'", 'to': "orm['auth.User']"}),
            'ctime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '765', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_delete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'waiter'", 'unique': 'True', 'to': "orm['auth.User']"})
        },
        'likeable.like': {
            'Meta': {'unique_together': "(('user', 'content_type', 'object_id'),)", 'object_name': 'Like'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'likes'", 'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['kinger']