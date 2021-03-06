# Generated by Django 2.0.1 on 2018-04-18 17:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Deploy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('deployed_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Fail_url_detail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('queue_url', models.CharField(blank=True, max_length=255, null=True)),
                ('spider_url', models.CharField(blank=True, max_length=255, null=True)),
                ('status_code', models.CharField(blank=True, max_length=11, null=True)),
                ('save_time', models.CharField(blank=True, max_length=50, null=True)),
                ('dept_id', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Invalid_task_url',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_id', models.CharField(blank=True, max_length=64, null=True)),
                ('dept_name_key', models.CharField(blank=True, max_length=64, null=True)),
                ('dept_id', models.IntegerField(blank=True, null=True)),
                ('item_title', models.CharField(blank=True, max_length=100, null=True)),
                ('item_content', models.TextField(blank=True, default=None, null=True)),
                ('item_pulishdate', models.CharField(blank=True, max_length=32, null=True)),
                ('item_contact', models.CharField(blank=True, max_length=200, null=True)),
                ('item_pricerange', models.CharField(blank=True, max_length=20, null=True)),
                ('item_deadline', models.CharField(blank=True, max_length=20, null=True)),
                ('item_submit_address', models.CharField(blank=True, max_length=100, null=True)),
                ('item_url', models.CharField(blank=True, max_length=255, null=True)),
                ('url_status', models.IntegerField(default=0)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('input_time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Item_monitor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_total', models.IntegerField(blank=True, null=True)),
                ('item_avail', models.IntegerField(blank=True, null=True)),
                ('item_invalid', models.IntegerField(blank=True, null=True)),
                ('item_avail_increased', models.IntegerField(blank=True, null=True)),
                ('agent_ip_port', models.CharField(blank=True, max_length=50, null=True)),
                ('start_time', models.DateTimeField(auto_now=True)),
                ('end_time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Monitor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default=None, max_length=255)),
                ('description', models.CharField(blank=True, default='', max_length=255)),
                ('type', models.CharField(blank=True, default='', max_length=255)),
                ('configuration', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('node_name', models.CharField(default=None, max_length=255)),
                ('node_ip', models.GenericIPAddressField(null=True)),
                ('node_port', models.IntegerField(blank=True, default=6800, null=True)),
                ('auth', models.IntegerField(blank=True, default=0, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('username', models.CharField(blank=True, max_length=255, null=True)),
                ('password', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('node_status', models.TextField(blank=True, null=True)),
                ('is_lock', models.IntegerField(blank=True, default=1, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spider_name', models.CharField(default=None, max_length=255)),
                ('spider_desc', models.CharField(blank=True, max_length=255, null=True)),
                ('egg', models.CharField(blank=True, max_length=255, null=True)),
                ('configuration', models.TextField(blank=True, null=True)),
                ('configurable', models.IntegerField(blank=True, default=0)),
                ('built_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('generated_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('sort', models.IntegerField(default=999)),
                ('is_lock', models.IntegerField(default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('node', models.ManyToManyField(through='zzh.Deploy', to='zzh.Node')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectRuler',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_name', models.CharField(blank=True, max_length=255, null=True)),
                ('project_desc', models.CharField(blank=True, max_length=255, null=True)),
                ('spider', models.CharField(blank=True, max_length=255, null=True)),
                ('dept_id', models.CharField(blank=True, default=None, max_length=11, null=True)),
                ('dept_name_key', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('url', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('spider_template', models.IntegerField(choices=[(1, ''), (2, ''), (3, '')], default=0, null=True, verbose_name='choices template')),
                ('func', models.TextField(blank=True, default=None, null=True)),
                ('is_lock', models.IntegerField(blank=True, default=1, null=True)),
                ('next_filter', models.CharField(blank=True, default='0', max_length=255, null=True)),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='PRO', to='zzh.Project')),
            ],
        ),
        migrations.CreateModel(
            name='Queue_url_monitor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_queue_url', models.IntegerField(blank=True, null=True)),
                ('success_queue_url', models.IntegerField(blank=True, null=True)),
                ('fail_queue_url', models.IntegerField(blank=True, null=True)),
                ('status_403_queue_url', models.IntegerField(blank=True, null=True)),
                ('status_404_queue_url', models.IntegerField(blank=True, null=True)),
                ('status_50x_queue_url', models.IntegerField(blank=True, null=True)),
                ('status_other_queue_url', models.IntegerField(blank=True, null=True)),
                ('agent_ip_port', models.CharField(blank=True, max_length=50, null=True)),
                ('start_time', models.DateTimeField(auto_now=True)),
                ('end_time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Scheduler',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('schedule_name', models.CharField(default=None, max_length=255)),
                ('schedule_desc', models.CharField(default=None, max_length=255)),
                ('spider_time', models.IntegerField(blank=True, default=30, null=True)),
                ('project_time', models.IntegerField(blank=True, default=30, null=True)),
                ('create_time', models.DateTimeField(auto_now=True)),
                ('is_lock', models.IntegerField(blank=True, default=1, null=True)),
                ('priority', models.IntegerField(default=999)),
                ('cron_minutes', models.CharField(default='0', max_length=20)),
                ('cron_hour', models.CharField(default='*', max_length=20)),
                ('cron_day_of_month', models.CharField(default='*', max_length=20)),
                ('cron_day_of_week', models.CharField(default='*', max_length=20)),
                ('cron_month', models.CharField(default='*', max_length=20)),
                ('enabled', models.IntegerField(default=0)),
                ('run_type', models.CharField(default='periodic', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Spider',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spider_name', models.CharField(default=None, max_length=255)),
                ('spider_desc', models.CharField(default=None, max_length=255)),
                ('sort', models.IntegerField(default=999)),
                ('create_time', models.DateTimeField(auto_now=True)),
                ('is_lock', models.IntegerField(blank=True, default=1, null=True)),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='zzh.Project')),
                ('scheduler', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='zzh.Scheduler')),
            ],
        ),
        migrations.CreateModel(
            name='Spider_url_monitor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_url', models.IntegerField(blank=True, null=True)),
                ('success_url', models.IntegerField(blank=True, null=True)),
                ('fail_url', models.IntegerField(blank=True, null=True)),
                ('status_403_url', models.IntegerField(blank=True, null=True)),
                ('status_404_url', models.IntegerField(blank=True, null=True)),
                ('status_50x_url', models.IntegerField(blank=True, null=True)),
                ('status_other_url', models.IntegerField(blank=True, null=True)),
                ('agent_ip_port', models.CharField(blank=True, max_length=50, null=True)),
                ('start_time', models.DateTimeField(auto_now=True)),
                ('end_time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='SpiderTemplates',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tem_type', models.CharField(blank=True, max_length=255, null=True)),
                ('tem_text', models.TextField(blank=True, default=None, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clients', models.TextField(blank=True, null=True)),
                ('project', models.CharField(blank=True, max_length=255, null=True)),
                ('spider', models.CharField(blank=True, max_length=255, null=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('args', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('trigger', models.CharField(blank=True, max_length=255, null=True)),
                ('success', models.IntegerField(blank=True, default=0)),
                ('error', models.IntegerField(blank=True, default=0)),
                ('last', models.DateTimeField(blank=True, null=True)),
                ('configuration', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Task_url',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_id', models.CharField(blank=True, max_length=64, null=True)),
                ('dept_name_key', models.CharField(blank=True, max_length=64, null=True)),
                ('dept_id', models.IntegerField(blank=True, null=True)),
                ('item_title', models.CharField(blank=True, max_length=100, null=True)),
                ('item_content', models.TextField(blank=True, default=None, null=True)),
                ('item_pulishdate', models.CharField(blank=True, max_length=32, null=True)),
                ('item_contact', models.CharField(blank=True, max_length=200, null=True)),
                ('item_pricerange', models.CharField(blank=True, max_length=20, null=True)),
                ('item_deadline', models.CharField(blank=True, max_length=20, null=True)),
                ('item_submit_address', models.CharField(blank=True, max_length=100, null=True)),
                ('item_url', models.CharField(blank=True, max_length=255, null=True)),
                ('url_status', models.IntegerField(default=0)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('input_time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='projectruler',
            name='scheduler',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='SCH', to='zzh.Scheduler'),
        ),
        migrations.AddField(
            model_name='project',
            name='scheduler',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='zzh.Scheduler'),
        ),
        migrations.AddField(
            model_name='deploy',
            name='node',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='zzh.Node'),
        ),
        migrations.AddField(
            model_name='deploy',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='zzh.Project'),
        ),
    ]
