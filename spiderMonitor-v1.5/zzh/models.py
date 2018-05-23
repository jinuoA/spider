# -*-coding:utf-8 -*-
# Create your models here.

from django.db import models
from django.db.models import CharField, GenericIPAddressField, IntegerField, TextField, DateTimeField, \
    ManyToManyField, ForeignKey


class Monitor(models.Model):
    name = CharField(max_length=255, default=None)
    description = CharField(max_length=255, default='', blank=True)
    type = CharField(max_length=255, default='', blank=True)
    configuration = TextField(default='', blank=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)


class Scheduler(models.Model):
    schedule_name = CharField(max_length=255, default=None)
    schedule_desc = CharField(max_length=255, default=None)
    spider_time = IntegerField(default=30, blank=True, null=True)
    project_time = IntegerField(default=30, blank=True, null=True)
    create_time = DateTimeField(auto_now=True)
    is_lock = IntegerField(default=1, blank=True, null=True)
    priority = IntegerField(default=999)
    cron_minutes = CharField(max_length=20,default="0")
    cron_hour = CharField(max_length=20,default="*")
    cron_day_of_month = CharField(max_length=20,default="*")
    cron_day_of_week = CharField(max_length=20,default="*")
    cron_month = CharField(max_length=20,default="*")
    enabled = IntegerField(default=0) #0/1
    run_type = CharField(max_length=20,default='periodic') # periodic/onetime




class Node(models.Model):
    node_name = CharField(max_length=255, default=None)
    node_ip = GenericIPAddressField(max_length=255, null=True)
    node_port = IntegerField(default=6800, blank=True, null=True)
    auth = IntegerField(default=0, blank=True, null=True)
    description = TextField(blank=True, null=True)
    username = CharField(max_length=255, blank=True, null=True)
    password = CharField(max_length=255, blank=True, null=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    node_status = TextField(blank=True, null=True)
    is_lock = IntegerField(default=1, blank=True, null=True)


class Project(models.Model):
    spider_name = CharField(max_length=255, default=None)
    spider_desc = CharField(max_length=255, null=True, blank=True)
    egg = CharField(max_length=255, null=True, blank=True)
    configuration = TextField(blank=True, null=True)
    configurable = IntegerField(default=0, blank=True)
    built_at = DateTimeField(default=None, blank=True, null=True)
    generated_at = DateTimeField(default=None, blank=True, null=True)
    sort = IntegerField(default=999)
    is_lock = IntegerField(default=1)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    node = ManyToManyField(Node, through='Deploy', unique=False)
    scheduler = ForeignKey(Scheduler, blank=True, null=True, on_delete=models.DO_NOTHING)


class ProjectRuler(models.Model):
    TEM_CHOICES = (
        (1, ""),
        (2, ""),
        (3, ""),
    )

    project_name = CharField(max_length=255,null=True, blank=True)
    project_desc = CharField(max_length=255,null=True, blank=True)
    spider = CharField(max_length=255, null=True, blank=True)
    dept_id = CharField(max_length=11, default=None, null=True, blank=True)
    dept_name_key = CharField(max_length=255, default=None, null=True, blank=True)
    url = CharField(max_length=255, default=None, null=True, blank=True)
    spider_template = IntegerField(default=0,choices=TEM_CHOICES,null=True, verbose_name='choices template')
    func = TextField(default=None, null=True, blank=True)
    is_lock = IntegerField(default=1, blank=True, null=True)
    next_filter = CharField(max_length=255, default='0', null=True, blank=True)
    project = ForeignKey(Project, blank=True, null=True, related_name='PRO', on_delete=models.DO_NOTHING)
    scheduler = ForeignKey(Scheduler, blank=True, null=True, related_name='SCH', on_delete=models.DO_NOTHING)


class SpiderTemplates(models.Model):
    tem_type = CharField(max_length=255,blank=True,null=True)
    tem_text = TextField(default=None, null=True, blank=True)


class Spider(models.Model):
    spider_name = CharField(max_length=255, default=None)
    spider_desc = CharField(max_length=255, default=None)
    sort = IntegerField(default=999)
    create_time = DateTimeField(auto_now=True)
    is_lock = IntegerField(default=1, blank=True, null=True)
    project = ForeignKey(Project, blank=True, null=True, on_delete=models.DO_NOTHING)
    scheduler = ForeignKey(Scheduler, blank=True, null=True, on_delete=models.DO_NOTHING)


class Deploy(models.Model):
    node = ForeignKey(Node, unique=False, on_delete=models.DO_NOTHING)
    project = ForeignKey(Project, unique=False, on_delete=models.DO_NOTHING)
    description = CharField(max_length=255, blank=True, null=True)
    deployed_at = DateTimeField(default=None, blank=True, null=True)
    created_at = DateTimeField(auto_now=True)
    updated_at = DateTimeField(auto_now_add=True)


class Task(models.Model):
    clients = TextField(null=True, blank=True)
    project = CharField(max_length=255, null=True, blank=True)
    spider = CharField(max_length=255, null=True, blank=True)
    name = CharField(max_length=255, null=True, blank=True)
    args = TextField(null=True, blank=True)
    description = TextField(null=True, blank=True)
    trigger = CharField(max_length=255, null=True, blank=True)
    success = IntegerField(default=0, blank=True)
    error = IntegerField(default=0, blank=True)
    last = DateTimeField(null=True, blank=True)
    configuration = TextField(null=True, blank=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)


class Fail_url_detail(models.Model):
    queue_url = CharField(max_length=255,blank=True,null=True)
    spider_url = CharField(max_length=255,blank=True,null=True)
    status_code = CharField(max_length=11,blank=True,null=True)
    # save_time = CharField(max_length=50,blank=True,null=True)
    save_time = DateTimeField(auto_now=True)
    dept_id = IntegerField(blank=True,null=True)
    dept_name_key = CharField(max_length=50,blank=True,null=True)


class Item_monitor(models.Model):
    item_total = IntegerField(blank=True,null=True)
    item_avail = IntegerField(blank=True,null=True)
    item_invalid = IntegerField(blank=True,null=True)
    item_avail_increased = IntegerField(blank=True,null=True)
    agent_ip_port = CharField(max_length=50,blank=True,null=True)
    start_time = DateTimeField(auto_now=True)
    end_time = DateTimeField(auto_now_add=True)


class Queue_url_monitor(models.Model):
    total_queue_url = IntegerField(blank=True,null=True)
    success_queue_url = IntegerField(blank=True,null=True)
    fail_queue_url = IntegerField(blank=True,null=True)
    status_403_queue_url = IntegerField(blank=True,null=True)
    status_404_queue_url = IntegerField(blank=True,null=True)
    status_50x_queue_url = IntegerField(blank=True,null=True)
    status_other_queue_url = IntegerField(blank=True,null=True)
    agent_ip_port = CharField(max_length=50, blank=True, null=True)
    start_time = DateTimeField(auto_now=True)
    end_time = DateTimeField(auto_now_add=True)


class Spider_url_monitor(models.Model):
    total_url = IntegerField(blank=True,null=True)
    success_url = IntegerField(blank=True,null=True)
    fail_url = IntegerField(blank=True,null=True)
    status_403_url = IntegerField(blank=True,null=True)
    status_404_url = IntegerField(blank=True,null=True)
    status_50x_url = IntegerField(blank=True,null=True)
    status_other_url = IntegerField(blank=True,null=True)
    agent_ip_port = CharField(max_length=50, blank=True, null=True)
    start_time = DateTimeField(auto_now=True)
    end_time = DateTimeField(auto_now_add=True)


class Task_url(models.Model):
    task_id = CharField(max_length=64,blank=True,null=True)
    dept_name_key = CharField(max_length=64,blank=True,null=True)
    dept_id = IntegerField(blank=True,null=True)
    item_title = CharField(max_length=100,blank=True,null=True)
    item_content = TextField(default=None,blank=True,null=True)
    item_pulishdate = CharField(max_length=32,blank=True,null=True)
    item_contact = CharField(max_length=200,blank=True,null=True)
    item_pricerange = CharField(max_length=20,blank=True,null=True)
    item_deadline = CharField(max_length=20,blank=True,null=True)
    item_submit_address = CharField(max_length=100,blank=True,null=True)
    item_url = CharField(max_length=255,blank=True,null=True)
    url_status = IntegerField(default=0)
    create_time = DateTimeField(auto_now=True)
    input_time = DateTimeField(auto_now_add=True)


class Invalid_task_url(models.Model):
    task_id = CharField(max_length=64, blank=True, null=True)
    dept_name_key = CharField(max_length=64, blank=True, null=True)
    dept_id = IntegerField(blank=True, null=True)
    item_title = CharField(max_length=100, blank=True, null=True)
    item_content = TextField(default=None, blank=True, null=True)
    item_pulishdate = CharField(max_length=32, blank=True, null=True)
    item_contact = CharField(max_length=200, blank=True, null=True)
    item_pricerange = CharField(max_length=20, blank=True, null=True)
    item_deadline = CharField(max_length=20, blank=True, null=True)
    item_submit_address = CharField(max_length=100, blank=True, null=True)
    item_url = CharField(max_length=255, blank=True, null=True)
    url_status = IntegerField(default=0)
    create_time = DateTimeField(auto_now=True)
    input_time = DateTimeField(auto_now_add=True)



