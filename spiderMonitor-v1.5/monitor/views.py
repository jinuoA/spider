# -*-coding:utf-8 -*-
import json
from django.shortcuts import render
from django.core.serializers import serialize
from django.utils import timezone
from zzh.response import JsonResponse
from zzh.models import Project, Deploy, Monitor, Spider, Scheduler, ProjectRuler, Node,Fail_url_detail,Item_monitor,\
    Queue_url_monitor,Spider_url_monitor, \
    SpiderTemplates,Task,Task_url,Invalid_task_url
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger
from django.db.models import F
from django.db.models import Q
from django.http import HttpResponse
from xlwt import *
from io import StringIO,BytesIO
from datetime import timedelta,date
import logging
import re
import datetime
from zzh import schedul



class CJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)


def itemMonitorDay(request):
    """
    :param request: request objects
    :param tim: time
    :return: json
    """
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        # {"startDay": "2018-04-20", "hour": "9"}
        # startDay = data["startDay"]
        startDay = datetime.datetime.now().strftime("%Y-%m-%d")
        hour = data["hour"]
        item_total_list = []
        item_avail_list = []
        item_invalid_list = []
        item_avail_increased_list = []
        for h in range(0,24):
            h = str(h)
            itemData = Item_monitor.objects.filter(start_time__startswith=startDay, start_time__hour=h)
            zzhTaskLi = Task_url.objects.filter(input_time__startswith=startDay, input_time__hour=h)
            if zzhTaskLi:
                item_avail_increased = zzhTaskLi.count()
                item_avail_increased_list.append(item_avail_increased)
            else:
                item_avail_increased = 0
                item_avail_increased_list.append(item_avail_increased)
            if itemData:
                item_total = item_avail = item_invalid = 0
                for item in itemData:
                    item_total = item.item_total + item_total
                    item_avail = item_avail + item.item_avail
                    item_invalid = item_invalid + item.item_invalid
                item_total_list.append(item_total)
                item_avail_list.append(item_avail)
                item_invalid_list.append(item_invalid)
            else:
                item_total = 0
                item_avail = 0
                item_invalid = 0
                item_total_list.append(item_total)
                item_avail_list.append(item_avail)
                item_invalid_list.append(item_invalid)
        monitor_list = {
            "item_total": item_total_list,
            "item_avail": item_avail_list,
            "item_invalid": item_invalid_list,
            "item_avail_increased": item_avail_increased_list,
        }
        return JsonResponse(monitor_list)


def itemMonitorMonth(request):
    """
    :param request: request objects
    :param tim: time
    :return: json
    """
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        # {"startDay": "2018-04-20", "hour": "9"}
        # month = data['month']
        # year = data['year']
        year = datetime.datetime.now().strftime("%Y")
        month = datetime.datetime.now().strftime("%m")
        item_total_list = []
        item_avail_list = []
        item_invalid_list = []
        item_avail_increased_list = []
        if re.match(r'\d+', year) and re.match(r'\d+', month):
            # ym_date = year + '-' + (month if int(month) > 9 else ('0' + month))
            ym_date = year + '-' + month
        for h in range(1,32):
            h = str(h)
            itemData = Item_monitor.objects.filter(start_time__startswith=ym_date, start_time__day=h)
            zzhTaskLi = Task_url.objects.filter(input_time__startswith=ym_date, input_time__day=h)
            if zzhTaskLi:
                item_avail_increased = zzhTaskLi.count()
                item_avail_increased_list.append(item_avail_increased)
            else:
                item_avail_increased = 0
                item_avail_increased_list.append(item_avail_increased)
            if itemData:
                item_total = item_avail = item_invalid = 0
                for item in itemData:
                    item_total = item.item_total + item_total
                    item_avail = item_avail + item.item_avail
                    item_invalid = item_invalid + item.item_invalid
                item_total_list.append(item_total)
                item_avail_list.append(item_avail)
                item_invalid_list.append(item_invalid)
            else:
                item_total = 0
                item_avail = 0
                item_invalid = 0
                item_total_list.append(item_total)
                item_avail_list.append(item_avail)
                item_invalid_list.append(item_invalid)
        monitor_list = {
            "item_total": item_total_list,
            "item_avail": item_avail_list,
            "item_invalid": item_invalid_list,
            "item_avail_increased": item_avail_increased_list,
        }
        return JsonResponse(monitor_list)

def itemMonitorWeek(request):
    if request.method == "GET":
        # data = json.loads(request.body.decode('utf-8'))
        # {"startDay": "2018-04-20", "hour": "9"}
        startTime = timezone.now()
        edate = int(datetime.datetime.now().strftime("%d"))
        sdate = edate-6
        item_total_list = []
        item_avail_list = []
        item_invalid_list = []
        item_avail_increased_list = []
        for d in range(sdate,edate+1):
            d = str(d)
            itemData = Item_monitor.objects.filter(start_time__range=(startTime - timedelta(days=6), startTime),
                                                   start_time__day=d)
            zzhTaskLi = Task_url.objects.filter(input_time__range=(startTime-timedelta(days=6),startTime),input_time__day=d)
            if zzhTaskLi:
                item_avail_increased = zzhTaskLi.count()
                item_avail_increased_list.append(item_avail_increased)
            else:
                item_avail_increased = 0
                item_avail_increased_list.append(item_avail_increased)
            if itemData:
                item_total = item_avail = item_invalid = 0
                for item in itemData:
                    item_total = item.item_total + item_total
                    item_avail = item_avail + item.item_avail
                    item_invalid = item_invalid + item.item_invalid
                item_total_list.append(item_total)
                item_avail_list.append(item_avail)
                item_invalid_list.append(item_invalid)
            else:
                item_total = 0
                item_avail = 0
                item_invalid = 0
                item_total_list.append(item_total)
                item_avail_list.append(item_avail)
                item_invalid_list.append(item_invalid)
        monitor_list = {
            "item_total": item_total_list,
            "item_avail": item_avail_list,
            "item_invalid": item_invalid_list,
            "item_avail_increased": item_avail_increased_list,
        }
        return JsonResponse(monitor_list)


def queueMonitorDay(request):
    """
    :param request: request objects
    :param tim: time
    :return: json
    """
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        # {"startDay": "2018-04-20", "hour": "9"}
        print(data)
        # startDay = data["startDay"]
        startDay = datetime.datetime.now().strftime("%Y-%m-%d")
        print(startDay)
        hour = data["hour"]
        total_queue_url_list = []
        success_queue_url_list = []
        fail_queue_url_list = []
        status_403_queue_url_list = []
        status_404_queue_url_list = []
        status_50x_queue_url_list = []
        status_other_queue_url_list = []
        for h in range(0,24):
            h = str(h)
            queueUrlData = Queue_url_monitor.objects.filter(start_time__startswith=startDay, start_time__hour=h)
            failDetailLi = Fail_url_detail.objects.filter(save_time__startswith=startDay, save_time__hour=h).values('status_code','queue_url','save_time').distinct()
            failDe = Fail_url_detail.objects.filter(save_time__startswith=startDay, save_time__hour=h,queue_url=F('spider_url'))
            if failDe:
                fail_queue_url = failDe.count()
                fail_queue_url_list.append(fail_queue_url)
            else:
                fail_queue_url = 0
                fail_queue_url_list.append(fail_queue_url)
            if failDetailLi:
                failQueueUrl_403 = failDetailLi.filter(status_code=403)
                status_403_queue_url = failQueueUrl_403.count()
                failQueueUrl_404 = failDetailLi.filter(status_code=404)
                status_404_queue_url = failQueueUrl_404.count()
                failQueueUrl_50x = failDetailLi.filter(status_code__in=(500,502))
                status_50x_queue_url = failQueueUrl_50x.count()
                failQueueUrl_other = failDetailLi.exclude(status_code__in=(403,404,500,502))
                status_other_queue_url = failQueueUrl_other.count()
                status_403_queue_url_list.append(status_403_queue_url)
                status_404_queue_url_list.append(status_404_queue_url)
                status_50x_queue_url_list.append(status_50x_queue_url)
                status_other_queue_url_list.append(status_other_queue_url)
            else:
                status_403_queue_url = 0
                status_404_queue_url = 0
                status_50x_queue_url = 0
                status_other_queue_url = 0
                status_403_queue_url_list.append(status_403_queue_url)
                status_404_queue_url_list.append(status_404_queue_url)
                status_50x_queue_url_list.append(status_50x_queue_url)
                status_other_queue_url_list.append(status_other_queue_url)
            if queueUrlData:
                total_queue_url = success_queue_url = 0
                for queue in queueUrlData:
                    total_queue_url = queue.total_queue_url + total_queue_url
                    success_queue_url = queue.success_queue_url + success_queue_url
                total_queue_url_list.append(total_queue_url)
                success_queue_url_list.append(success_queue_url)
            else:
                total_queue_url = 0
                success_queue_url = 0
                total_queue_url_list.append(total_queue_url)
                success_queue_url_list.append(success_queue_url)
        monitor_list = {
            "total_queue_url": total_queue_url_list,
            "success_queue_url": success_queue_url_list,
            "fail_queue_url": fail_queue_url_list,
            "status_403_queue_url": status_403_queue_url_list,
            "status_404_queue_url": status_404_queue_url_list,
            "status_50x_queue_url": status_50x_queue_url_list,
            "status_other_queue_url": status_other_queue_url_list
        }
        return JsonResponse(monitor_list)


def spiderMonitorDay(request):
    """
    :param request: request objects
    :param tim: time
    :return: json
    """
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        # {"startDay": "2018-04-20", "hour": "9"}
        # startDay = data["startDay"]
        startDay = datetime.datetime.now().strftime("%Y-%m-%d")
        hour = data["hour"]
        total_url_list = []
        success_url_list = []
        fail_url_list = []
        status_403_url_list = []
        status_404_url_list = []
        status_50x_url_list = []
        status_other_url_list = []
        for h in range(0,24):
            h = str(h)
            spiderUrlData = Spider_url_monitor.objects.filter(start_time__startswith=startDay, start_time__hour=h)
            failUrlli = Fail_url_detail.objects.filter(save_time__startswith=startDay, save_time__hour=h)
            failUr = Fail_url_detail.objects.filter(save_time__startswith=startDay, save_time__hour=h)
            if failUr:
                fail_url = failUr.count()
                fail_url_list.append(fail_url)
            else:
                fail_url = 0
                fail_url_list.append(fail_url)
            if failUrlli:
                fail_url_403 = failUrlli.filter(status_code=403)
                status_403_url = fail_url_403.count()
                fail_url_404 = failUrlli.filter(status_code=404)
                status_404_url = fail_url_404.count()
                fail_url_50x = failUrlli.filter(status_code__in=(500,502))
                status_50x_url = fail_url_50x.count()
                fail_othor_url = failUrlli.exclude(status_code__in=(403,404,500,502))
                status_other_url = fail_othor_url.count()
                status_403_url_list.append(status_403_url)
                status_404_url_list.append(status_404_url)
                status_50x_url_list.append(status_50x_url)
                status_other_url_list.append(status_other_url)
            else:
                status_403_url = 0
                status_404_url = 0
                status_50x_url = 0
                status_other_url = 0
                status_403_url_list.append(status_403_url)
                status_404_url_list.append(status_404_url)
                status_50x_url_list.append(status_50x_url)
                status_other_url_list.append(status_other_url)
            if spiderUrlData:
                total_url = success_url = 0
                for url in spiderUrlData:
                    total_url = url.total_url + total_url
                    success_url = url.success_url + success_url
                total_url_list.append(total_url)
                success_url_list.append(success_url)
            else:
                total_url = 0
                success_url = 0
                total_url_list.append(total_url)
                success_url_list.append(success_url)
        monitor_list = {
            "total_url": total_url_list,
            "success_url": success_url_list,
            "fail_url": fail_url_list,
            "status_403_url": status_403_url_list,
            "status_404_url": status_404_url_list,
            "status_50x_url": status_50x_url_list,
            "status_other_url": status_other_url_list,
        }
        return JsonResponse(monitor_list)



def monitorWeek(request):
    """
    :param request:
    :return: json
    """
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        startTime = timezone.now()
        # startTime = startTime+timedelta(hours=8)
        # startTime = datetime.datetime.now()
        # startTime = datetime.datetime.utcfromtimestamp(time.mktime(startTime.timetuple()))
        print(startTime)
        print(startTime+timedelta(days=6))
        day = int(data['day'])
        item_total_list = []
        item_avail_list = []
        item_invalid_list = []
        item_avail_increased_list = []
        total_queue_url_list = []
        success_queue_url_list = []
        fail_queue_url_list = []
        status_403_queue_url_list = []
        status_404_queue_url_list = []
        status_50x_queue_url_list = []
        status_other_queue_url_list = []
        total_url_list = []
        success_url_list = []
        fail_url_list = []
        status_403_url_list = []
        status_404_url_list = []
        status_50x_url_list = []
        status_other_url_list = []
        for d in range(1,8):
            itemData = Item_monitor.objects.filter(start_time__range=(startTime-timedelta(days=6),startTime),start_time__week_day=d)
            queueUrlData = Queue_url_monitor.objects.filter(start_time__range=(startTime-timedelta(days=6),startTime),start_time__week_day=d)
            spiderUrlData = Spider_url_monitor.objects.filter(start_time__range=(startTime-timedelta(days=6),startTime),start_time__week_day=d)
            zzhTaskLi = Task_url.objects.filter(input_time__range=(startTime-timedelta(days=6),startTime), input_time__hour=d)
            item_avail_increased = zzhTaskLi.count()
            failDetailLi = Fail_url_detail.objects.filter(save_time__range=(startTime-timedelta(days=6),startTime),save_time__week_day=d).values(
                'queue_url', 'status_code').distinct()
            fail_queue_url = failDetailLi.count()
            failQueueUrl_403 = failDetailLi.filter(status_code=403)
            status_403_queue_url = failQueueUrl_403.count()
            failQueueUrl_404 = failDetailLi.filter(status_code=404)
            status_404_queue_url = failQueueUrl_404.count()
            failQueueUrl_50x = failDetailLi.filter(status_code__in=(500, 502))
            status_50x_queue_url = failQueueUrl_50x.count()
            failQueueUrl_other = failDetailLi.exclude(status_code__in=(403, 404, 500, 502))
            status_other_queue_url = failQueueUrl_other.count()
            failUrlli = Fail_url_detail.objects.filter(save_time__range=(startTime-timedelta(days=6),startTime),save_time__week_day=d).values(
                'spider_url', 'status_code').distinct()
            fail_url = failUrlli.count()
            fail_url_403 = failUrlli.filter(status_code=403)
            status_403_url = fail_url_403.count()
            fail_url_404 = failUrlli.filter(status_code=404)
            status_404_url = fail_url_404.count()
            fail_url_50x = failUrlli.filter(status_code__in=(500, 502))
            status_50x_url = fail_url_50x.count()
            fail_othor_url = failUrlli.exclude(status_code__in=(403, 404, 500, 502))
            status_other_url = fail_othor_url.count()
            item_total = item_avail = item_invalid = 0
            total_queue_url = success_queue_url = 0
            total_url = success_url = 0
            for item, queue, url in zip(itemData, queueUrlData, spiderUrlData):
                item_total = item.item_total + item_total
                item_avail = item_avail + item.item_avail
                item_invalid = item_invalid + item.item_invalid
                total_queue_url = queue.total_queue_url + total_queue_url
                success_queue_url = queue.success_queue_url + success_queue_url
                total_url = url.total_url + total_url
                success_url = url.success_url + success_url
            item_total_list.append(item_total)
            item_avail_list.append(item_avail)
            item_invalid_list.append(item_invalid)
            item_avail_increased_list.append(item_avail_increased)
            total_queue_url_list.append(total_queue_url)
            success_queue_url_list.append(success_queue_url)
            fail_queue_url_list.append(fail_queue_url)
            status_403_queue_url_list.append(status_403_queue_url)
            status_404_queue_url_list.append(status_404_queue_url)
            status_50x_queue_url_list.append(status_50x_queue_url)
            status_other_queue_url_list.append(status_other_queue_url)
            total_url_list.append(total_url)
            success_url_list.append(success_url)
            fail_url_list.append(fail_url)
            status_403_url_list.append(status_403_url)
            status_404_url_list.append(status_404_url)
            status_50x_url_list.append(status_50x_url)
            status_other_url_list.append(status_other_url)
        monitor_list = {
            "item_total": item_total_list,
            "item_avail": item_avail_list,
            "item_invalid": item_invalid_list,
            "item_avail_increased": item_avail_increased_list,
            "total_queue_url": total_queue_url_list,
            "success_queue_url": success_queue_url_list,
            "fail_queue_url": fail_queue_url_list,
            "status_403_queue_url": status_403_queue_url_list,
            "status_404_queue_url": status_404_queue_url_list,
            "status_50x_queue_url": status_50x_queue_url_list,
            "status_other_queue_url": status_other_queue_url_list,
            "total_url": total_url_list,
            "success_url": success_url_list,
            "fail_url": fail_url_list,
            "status_403_url": status_403_url_list,
            "status_404_url": status_404_url_list,
            "status_50x_url": status_50x_url_list,
            "status_other_url": status_other_url_list,

        }
        return JsonResponse(monitor_list)


def monitorMonth(request):
    """
    :param request:
    :return: json
    """
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        # mon = int(data['month'])
        month = data['month']
        year = data['year']
        day = int(data['day'])
        item_total_list = []
        item_avail_list = []
        item_invalid_list = []
        item_avail_increased_list = []
        total_queue_url_list = []
        success_queue_url_list = []
        fail_queue_url_list = []
        status_403_queue_url_list = []
        status_404_queue_url_list = []
        status_50x_queue_url_list = []
        status_other_queue_url_list = []
        total_url_list = []
        success_url_list = []
        fail_url_list = []
        status_403_url_list = []
        status_404_url_list = []
        status_50x_url_list = []
        status_other_url_list = []
        if re.match(r'\d+', year) and re.match(r'\d+', month):
            ym_date = year + '-' + (month if int(month) > 9 else ('0' + month))
            for d in range(1,32):
                itemData = Item_monitor.objects.filter(start_time__startswith=ym_date,start_time__day=d)
                queueUrlData = Queue_url_monitor.objects.filter(start_time__startswith=ym_date,start_time__day=d)
                spiderUrlData = Spider_url_monitor.objects.filter(start_time__startswith=ym_date,start_time__day=d)
                zzhTaskLi = Task_url.objects.filter(input_time__startswith=ym_date,input_time__day=d)
                item_avail_increased = zzhTaskLi.count()
                failDetailLi = Fail_url_detail.objects.filter(save_time__startswith=ym_date, save_time__day=d).values(
                    'queue_url','status_code').distinct()
                fail_queue_url = failDetailLi.count()
                failQueueUrl_403 = failDetailLi.filter(status_code=403)
                status_403_queue_url = failQueueUrl_403.count()
                failQueueUrl_404 = failDetailLi.filter(status_code=404)
                status_404_queue_url = failQueueUrl_404.count()
                failQueueUrl_50x = failDetailLi.filter(status_code__in=(500, 502))
                status_50x_queue_url = failQueueUrl_50x.count()
                failQueueUrl_other = failDetailLi.exclude(status_code__in=(403, 404, 500, 502))
                status_other_queue_url = failQueueUrl_other.count()
                failUrlli = Fail_url_detail.objects.filter(save_time__startswith=ym_date, save_time__hour=23).values(
                    'spider_url','status_code').distinct()
                fail_url = failUrlli.count()
                fail_url_403 = failUrlli.filter(status_code=403)
                status_403_url = fail_url_403.count()
                fail_url_404 = failUrlli.filter(status_code=404)
                status_404_url = fail_url_404.count()
                fail_url_50x = failUrlli.filter(status_code__in=(500, 502))
                status_50x_url = fail_url_50x.count()
                fail_othor_url = failUrlli.exclude(status_code__in=(403, 404, 500, 502))
                status_other_url = fail_othor_url.count()
                item_total = item_avail = item_invalid = 0
                total_queue_url = success_queue_url = 0
                total_url = success_url = 0
                for item, queue, url in zip(itemData, queueUrlData, spiderUrlData):
                    item_total = item.item_total + item_total
                    item_avail = item_avail + item.item_avail
                    item_invalid = item_invalid + item.item_invalid
                    total_queue_url = queue.total_queue_url + total_queue_url
                    success_queue_url = queue.success_queue_url + success_queue_url
                    total_url = url.total_url + total_url
                    success_url = url.success_url + success_url
                item_total_list.append(item_total)
                item_avail_list.append(item_avail)
                item_invalid_list.append(item_invalid)
                item_avail_increased_list.append(item_avail_increased)
                total_queue_url_list.append(total_queue_url)
                success_queue_url_list.append(success_queue_url)
                fail_queue_url_list.append(fail_queue_url)
                status_403_queue_url_list.append(status_403_queue_url)
                status_404_queue_url_list.append(status_404_queue_url)
                status_50x_queue_url_list.append(status_50x_queue_url)
                status_other_queue_url_list.append(status_other_queue_url)
                total_url_list.append(total_url)
                success_url_list.append(success_url)
                fail_url_list.append(fail_url)
                status_403_url_list.append(status_403_url)
                status_404_url_list.append(status_404_url)
                status_50x_url_list.append(status_50x_url)
                status_other_url_list.append(status_other_url)
            monitor_list = {
                "item_total": item_total_list,
                "item_avail": item_avail_list,
                "item_invalid": item_invalid_list,
                "item_avail_increased": item_avail_increased_list,
                "total_queue_url": total_queue_url_list,
                "success_queue_url": success_queue_url_list,
                "fail_queue_url": fail_queue_url_list,
                "status_403_queue_url": status_403_queue_url_list,
                "status_404_queue_url": status_404_queue_url_list,
                "status_50x_queue_url": status_50x_queue_url_list,
                "status_other_queue_url": status_other_queue_url_list,
                "total_url": total_url_list,
                "success_url": success_url_list,
                "fail_url": fail_url_list,
                "status_403_url": status_403_url_list,
                "status_404_url": status_404_url_list,
                "status_50x_url": status_50x_url_list,
                "status_other_url": status_other_url_list,

            }
            return JsonResponse(monitor_list)


def addTemplate(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        item_list_xpath = data['item_list_xpath']
        item_title_xpath = data['item_title_xpath']
        item_url_xpath = data['item_url_xpath']
        item_publishdata_xpath = data['item_publishdata_xpath']
        next_page_xpath = data['next_page_xpath']
        select_template = data['select_template']

        if next_page_xpath and item_list_xpath and item_title_xpath and item_url_xpath and item_publishdata_xpath:
            templateList = SpiderTemplates.objects.filter(tem_type=select_template).values()
            template = templateList.first().get('tem_text')
            next_page = re.findall(r'next_page_xpath = u"(.*)"', template)
            item_list = re.findall(r'list_xpath = "(.*)"', template)
            item_title = re.findall(r'title_xpath = "(.*)"', template)
            item_url = re.findall(r'url_xpath = "(.*)"', template)
            item_publishdata = re.findall(r'pdate_xpath = "(.*)"', template)
            func = template.replace(next_page[0],next_page_xpath).replace(item_list[0],item_list_xpath).replace(item_title[0],item_title_xpath).replace(item_url[0], item_url_xpath).replace(item_publishdata[0],item_publishdata_xpath)
            print(func)
            try:
                return JsonResponse({'func':func})
            except:
                return JsonResponse({'messages':'input error'})
        else:
            return JsonResponse({'messages':'input error'})


def failUrlList(request):
    if request.method == "GET":
        try:
            failUrlList  = Fail_url_detail.objects.all().order_by('-save_time')
            return JsonResponse({'failUrlList':failUrlList})
        except:
            return JsonResponse({'message':'not data'})


def FailUrlSearch(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        search_keywords = data.get('save_time') or data.get('queue_url') or data.get('spider_url') or data.get('status_code') or data.get('dept_id')
        if search_keywords:
            all_orgs = Fail_url_detail.objects.filter(
                Q(save_time__icontains=search_keywords) | Q(queue_url__icontains=search_keywords) \
                | Q(spider_url__icontains=search_keywords) |Q(status_code__icontains=search_keywords) \
                | Q(dept_id__icontains=search_keywords))
            try:
                while True:
                    return JsonResponse(all_orgs)
            except:
                return JsonResponse({'message': 'Project does not exist'})
        else:
            return JsonResponse({'message': 'Error'})


def taskUrlSearch(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        search_keywords = data.get('dept_name_key') or data.get('item_pulishdate')
        if search_keywords:
            all_orgs = Task_url.objects.filter(Q(dept_name_key=search_keywords) |Q(item_pulishdate__contains=search_keywords))
            all_orgs = json.loads(serialize('json',all_orgs))
            all_orgs = [dict(x["fields"], **{"id": x["pk"]}) for x in all_orgs]
            try:
                return JsonResponse(all_orgs)
            except:
                return JsonResponse({'message': 'data does not exist'})
        else:
            return JsonResponse({'message': 'Error'})


def failUrlLists(request):
    """
    feil url detail search
    """
    if request.method == "GET":
        failUrl = Fail_url_detail.objects.all()
        fail = []
        for fai in failUrl:
            queue_url = fai.queue_url
            fail.append(queue_url)
        projectDetails = ProjectRuler.objects.filter(url__in=fail)
        return JsonResponse(projectDetails)



def failUrlDetail(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        dept_id = data.get('dept_id')
        projectDetail = ProjectRuler.objects.filter(dept_id=dept_id)
        return JsonResponse(projectDetail)




def scheduler_run_ruler(request, scheduler_id):
    """
    start scheduler task
    :param request:
    :param scheduler_id:
    :return:
    """
    if request.method == "GET":
        from zzh.scheduler.sched import reload_runnable_spider_job_execution
        schedul.add_job(reload_runnable_spider_job_execution, 'interval', minutes=2, id='my_scheduler_job')
        schedule = Scheduler.objects.get(id=scheduler_id)
        spider_time = schedule.spider_time
        print(spider_time)
        # try:
        #     while True:
        #         schedul.start()
        #         time.sleep(2)
        # except (KeyboardInterrupt, SystemExit):
        #     schedul.shutdown()
        #     schedul.start()
        schedul.start()
        return JsonResponse({'result': 1})


def close_scheduler(request):
    """
    close scheduled task
    :return: bool
    """
    if request.method == "GET":
        log = logging.getLogger('apscheduler.executors.default')
        log.setLevel(logging.DEBUG)  # DEBUG
        fmt = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
        h = logging.StreamHandler()
        h.setFormatter(fmt)
        log.addHandler(h)
        job_id = 'my_scheduler_job'
        running_job_ids = set([job.id for job in schedul.get_jobs()])
        print(running_job_ids)
        if job_id in running_job_ids:
            print('start to do it')
            schedul.remove_job(job_id)
            schedul.shutdown()
        else:
            return JsonResponse({'messages':'Scheduling does not exist'})
    return JsonResponse({'result':1,'message':'Close scheduled task'})


def avalidItem(request):
    # avalidItemList = Task_url.objects.filter(input_time__startswith="2018-05-02", input_time__hour=16)
    dateTime = datetime.datetime.now().strftime("%Y-%m-%d")
    avalidItemList = Task_url.objects.filter(input_time__startswith=dateTime).order_by('dept_name_key')
    total_data = avalidItemList.count()
    paginator = Paginator(avalidItemList,25)
    # 从前端获取当前的页码数,默认为1
    page = request.GET.get('page', 1)
    # 把当前的页码数转换成整数类型
    currentPage = int(page)
    try:
        print(page)
        avalidItemList = paginator.page(page)  # 获取当前页码的记录
    except PageNotAnInteger:
        avalidItemList = paginator.page(1)  # 如果用户输入的页码不是整数时,显示第1页的内容
    except EmptyPage:
        avalidItemList = paginator.page(paginator.num_pages)  # 如果用户输入的页数不在系统的页码列表中时,显示最后一页的内容
    fail = []
    if avalidItemList:
        for fai in avalidItemList:
            dept_name_key = fai.dept_name_key
            projectDetail = ProjectRuler.objects.filter(dept_name_key=dept_name_key).values('project_desc').first()
            if projectDetail:
                fail.append(projectDetail['project_desc'])
        avalidItemLi = zip(avalidItemList, fail)
        return render(request,'item_avalid.html',{"avalidItemLi":avalidItemLi,"total_data":total_data,
                                                  "avalidItemList":avalidItemList})
    else:
        return JsonResponse({'messages':'not data'})


def fail_url(request):
    # avalidItemList = Task_url.objects.filter(input_time__startswith="2018-05-02", input_time__hour=16)
    # failQueueUrlList = Fail_url_detail.objects.filter(save_time__startswith="2018-05-03",save_time__hour=14,queue_url=F('spider_url')).order_by('save_time')
    dateTime = timezone.now().strftime("%Y-%m-%d")
    hour = int(datetime.datetime.now().strftime("%H"))
    failUrlList = Fail_url_detail.objects.filter(save_time__startswith=dateTime,
                                                 save_time__hour=hour).order_by('save_time')
    total_fail_data = failUrlList.count()
    paginator = Paginator(failUrlList, 20)
    # 从前端获取当前的页码数,默认为1
    page = request.GET.get('page', 1)
    # 把当前的页码数转换成整数类型
    currentPage = int(page)
    try:
        print(page)
        failUrlList = paginator.page(page)  # 获取当前页码的记录
    except PageNotAnInteger:
        failUrlList = paginator.page(1)  # 如果用户输入的页码不是整数时,显示第1页的内容
    except EmptyPage:
        failUrlList = paginator.page(paginator.num_pages)  # 如果用户输入的页数不在系统的页码列表中时,显示最后一页的内容
    fail = []
    if failUrlList:
        for fai in failUrlList:
            dept_name_key = fai.dept_name_key
            projectDetail = ProjectRuler.objects.filter(dept_name_key=dept_name_key).values('project_desc').first()
            if projectDetail:
                fail.append(projectDetail['project_desc'])
    failList = zip(failUrlList,fail)
    return render(request,'fail.html',{"failList":failList,"total_fail_data":total_fail_data,"failUrlList":failUrlList})


def excel_export(request):
    """
    导出excel表格
    """
    list_obj = ProjectRuler.objects.all().order_by("dept_id")
    if list_obj:
        # 创建工作薄
        ws = Workbook(encoding='utf-8')
        w = ws.add_sheet(u"爬虫脚本")
        w.write(0, 0, "id")
        w.write(0, 1, u"部门id")
        w.write(0, 2, u"部门名称")
        w.write(0, 3, u"项目描述")
        w.write(0, 4, u"初始url")
        # 写入数据
        excel_row = 1
        for obj in list_obj:
            data_id = obj.id
            data_dept_id = obj.dept_id
            data_dept_name_key = obj.dept_name_key
            data_project_name = obj.project_name
            dada_url = obj.url
            w.write(excel_row, 0, data_id)
            w.write(excel_row, 1, data_dept_id)
            w.write(excel_row, 2, data_dept_name_key)
            w.write(excel_row, 3, data_project_name)
            w.write(excel_row, 4, dada_url)
            excel_row += 1
        ###########################
        # exist_file = os.path.exists("test.xls")
        # if exist_file:
        #     os.remove(r"test.xls")
        # ws.save("test.xls")
        ############################
        sio = BytesIO()
        ws.save(sio)
        sio.seek(0)
        response = HttpResponse(sio.getvalue(), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=test.xls'
        response.write(sio.getvalue())
        return response


def excel_export_url(request):
    """
    导出失败urlexcel表格
    """
    dateTime = timezone.now().strftime("%Y-%m-%d")
    hour = int(datetime.datetime.now().strftime("%H"))
    failUrlList = Fail_url_detail.objects.filter(save_time__startswith=dateTime, save_time__hour=hour).order_by(
        'save_time')
    fail = []
    if failUrlDetail:
        for fai in failUrlList:
            dept_name_key = fai.dept_name_key
            projectDetail = ProjectRuler.objects.filter(dept_name_key=dept_name_key).values('project_desc').first()
            if projectDetail:
                fail.append(projectDetail['project_desc'])
    else:
        pass
    failList = zip(failUrlList, fail)
    if failList:
        # 创建工作薄
        ws = Workbook(encoding='utf-8')
        w = ws.add_sheet(u"失败url")
        w.write(0, 0, "项目描述")
        w.write(0, 1, u"部门名称")
        w.write(0, 2, u"部门id")
        w.write(0, 3, u"队列url")
        w.write(0, 4, u"url")
        w.write(0, 5, u"状态码")
        # 写入数据
        excel_row = 1
        for obj,p in failList:
            data_project_desc = p
            data_dept_id = obj.dept_id
            data_dept_name_key = obj.dept_name_key
            data_queue_url = obj.queue_url
            data_spider_url = obj.spider_url
            data_status_code = obj.status_code
            w.write(excel_row, 0, data_project_desc)
            w.write(excel_row, 1, data_dept_name_key)
            w.write(excel_row, 2, data_dept_id)
            w.write(excel_row, 3, data_queue_url)
            w.write(excel_row, 4, data_spider_url)
            w.write(excel_row, 5, data_status_code)
            excel_row += 1
        ###########################
        # exist_file = os.path.exists("test.xls")
        # if exist_file:
        #     os.remove(r"test.xls")
        # ws.save("test.xls")
        ############################
        sio = BytesIO()
        ws.save(sio)
        sio.seek(0)
        response = HttpResponse(sio.getvalue(), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="%s".xls' % "20180508失败url表"
        response.write(sio.getvalue())
        return response


def item_monitor(request):
    # avalidItemList = Task_url.objects.filter(input_time__startswith="2018-05-02", input_time__hour=16)
    dateTime = datetime.datetime.now().strftime("%Y-%m-%d")
    print(dateTime)
    avalidItemList = Task_url.objects.filter(input_time__startswith=dateTime).order_by('dept_name_key')
    # print(avalidItemList.values_list())
    total_data = avalidItemList.count()
    paginator = Paginator(avalidItemList, 10)

    # 从前端获取当前的页码数,默认为1
    page = request.GET.get('page', 1)

    # 把当前的页码数转换成整数类型
    currentPage = int(page)
    try:
        print(page)
        avalidItemList = paginator.page(page)  # 获取当前页码的记录
    except PageNotAnInteger:
        avalidItemList = paginator.page(1)  # 如果用户输入的页码不是整数时,显示第1页的内容
    except EmptyPage:
        avalidItemList = paginator.page(paginator.num_pages)  # 如果用户输入的页数不在系统的页码列表中时,显示最后一页的内容
    fail = []
    for fai in avalidItemList:
        dept_name_key = fai.dept_name_key
        projectDetail = ProjectRuler.objects.filter(dept_name_key=dept_name_key).values('project_desc').first()
        if projectDetail:
            fail.append(projectDetail['project_desc'])
    avalidItemLi = zip(avalidItemList,fail)
    return render(request, 'item_monitor.html',{"avalidItemLi": avalidItemLi, "total_data": total_data,
         "avalidItemList": avalidItemList})


def queue_monitor(request):
    # avalidItemList = Task_url.objects.filter(input_time__startswith="2018-05-02", input_time__hour=16)
    # failQueueUrlList = Fail_url_detail.objects.filter(save_time__startswith="2018-05-03",save_time__hour=14,queue_url=F('spider_url')).order_by('save_time')
    dateTime = timezone.now().strftime("%Y-%m-%d")
    hour = int(datetime.datetime.now().strftime("%H"))
    failUrlList = Fail_url_detail.objects.filter(save_time__startswith=dateTime, save_time__hour=hour,
                                                 queue_url=F('spider_url')).order_by('dept_name_key').distinct()
    total_fail_data = failUrlList.count()
    total_queue_fail_data = failUrlList.count()


    paginator = Paginator(failUrlList, 10)

    # 从前端获取当前的页码数,默认为1
    page = request.GET.get('page', 1)

    # 把当前的页码数转换成整数类型
    currentPage = int(page)
    try:
        print(page)
        failUrlList = paginator.page(page)  # 获取当前页码的记录
    except PageNotAnInteger:
        failUrlList = paginator.page(1)  # 如果用户输入的页码不是整数时,显示第1页的内容
    except EmptyPage:
        failUrlList = paginator.page(paginator.num_pages)  # 如果用户输入的页数不在系统的页码列表中时,显示最后一页的内容
    fail = []
    if failUrlList:
        for fai in failUrlList:
            dept_name_key = fai.dept_name_key
            projectDetail = ProjectRuler.objects.filter(dept_name_key=dept_name_key).values('project_desc').first()
            if projectDetail:
                fail.append(projectDetail['project_desc'])
    failList = zip(failUrlList, fail)
    return render(request, 'queue_monitor.html', {"failList": failList, "total_fail_data": total_fail_data,
                                        "total_queue_fail_data": total_queue_fail_data,"failUrlList":failUrlList})




def spider_monitor(request):
    dateTime = timezone.now().strftime("%Y-%m-%d")
    hour = int(datetime.datetime.now().strftime("%H"))
    failUrlList = Fail_url_detail.objects.filter(save_time__startswith=dateTime,save_time__hour=hour).order_by(
        'dept_name_key').distinct()
    fail = []
    for fai in failUrlList:
        dept_name_key = fai.dept_name_key
        projectDetail = ProjectRuler.objects.filter(dept_name_key=dept_name_key).values('project_desc').first()
        fail.append(projectDetail['project_desc'])
    total_fail_data = failUrlList.count()
    total_queue_fail_data = failUrlList.count()
    failList = zip(failUrlList, fail)
    return render(request, 'queue_monitor.html', {"failList": failList, "total_fail_data": total_fail_data,
                                                  "total_queue_fail_data": total_queue_fail_data})
"""
class Month_monitor(object):
    def __init__(self,request):
        self.item_total_list = []
        self.item_avail_list = []
        self.item_invalid_list = []
        self.item_avail_increased_list = []
        self.total_queue_url_list = []
        self.success_queue_url_list = []
        self.fail_queue_url_list = []
        self.status_403_queue_url_list = []
        self.status_404_queue_url_list = []
        self.status_50x_queue_url_list = []
        self.status_other_queue_url_list = []
        self.total_url_list = []
        self.success_url_list = []
        self.fail_url_list = []
        self.status_403_url_list = []
        self.status_404_url_list = []
        self.status_50x_url_list = []
        self.status_other_url_list = []


    def month_item_monitor(self,request):
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))
            # {"startDay": "2018-04-20", "hour": "9"}
            startDay = data["startDay"]
            hour = data["hour"]
            for h in range(0, 24):
                h = str(h)
                itemData = Item_monitor.objects.filter(start_time__startswith=startDay, start_time__hour=h)
                zzhTaskLi = Task_url.objects.filter(input_time__startswith=startDay, input_time__hour=h)
                item_avail_increased = zzhTaskLi.count()
                item_total = item_avail = item_invalid = 0
                for item in itemData:
                    item_total = item.item_total + item_total
                    item_avail = item_avail + item.item_avail
                    item_invalid = item_invalid + item.item_invalid
                self.item_total_list.append(item_total)
                self.item_avail_list.append(item_avail)
                self.item_invalid_list.append(item_invalid)
                self.item_avail_increased_list.append(item_avail_increased)
            monitor_list = {
                "item_total": self.item_total_list,
                "item_avail": self.item_avail_list,
                "item_invalid": self.item_invalid_list,
                "item_avail_increased": self.item_avail_increased_list,
            }
            return JsonResponse(monitor_list)

"""



def item_monitor_month(request):
    # avalidItemList = Task_url.objects.filter(input_time__startswith="2018-05-02", input_time__hour=16)
    dateTime = datetime.datetime.now().strftime("%Y-%m")
    print(dateTime)
    avalidItemList = Task_url.objects.filter(input_time__startswith=dateTime).order_by('dept_name_key')
    # print(avalidItemList.values_list())
    total_data = avalidItemList.count()
    paginator = Paginator(avalidItemList, 10)

    # 从前端获取当前的页码数,默认为1
    page = request.GET.get('page', 1)

    # 把当前的页码数转换成整数类型
    currentPage = int(page)
    try:
        print(page)
        avalidItemList = paginator.page(page)  # 获取当前页码的记录
    except PageNotAnInteger:
        avalidItemList = paginator.page(1)  # 如果用户输入的页码不是整数时,显示第1页的内容
    except EmptyPage:
        avalidItemList = paginator.page(paginator.num_pages)  # 如果用户输入的页数不在系统的页码列表中时,显示最后一页的内容
    return render(request, 'month_item_monitor.html',
                  {"avalidItemList": avalidItemList, "total_data":total_data})



def item_monitor_week(request):
    # avalidItemList = Task_url.objects.filter(input_time__startswith="2018-05-02", input_time__hour=16)
    startTime = timezone.now()
    avalidItemList = Task_url.objects.filter(input_time__range=(startTime - timedelta(days=6),
                                                                startTime)).order_by('-input_time')
    total_data = avalidItemList.count()
    # print(avalidItemList.values_list())
    paginator = Paginator(avalidItemList, 10)
    # 从前端获取当前的页码数,默认为1
    page = request.GET.get('page', 1)

    # 把当前的页码数转换成整数类型
    currentPage = int(page)
    try:
        print(page)
        avalidItemList = paginator.page(page)  # 获取当前页码的记录
    except PageNotAnInteger:
        avalidItemList = paginator.page(1)  # 如果用户输入的页码不是整数时,显示第1页的内容
    except EmptyPage:
        avalidItemList = paginator.page(paginator.num_pages)  # 如果用户输入的页数不在系统的页码列表中时,显示最后一页的内容
    fail = []
    for fai in avalidItemList:
        dept_name_key = fai.dept_name_key
        projectDetail = ProjectRuler.objects.filter(dept_name_key=dept_name_key).values('project_desc').first()
        if projectDetail:
            fail.append(projectDetail['project_desc'])
    avalidItemLi = zip(avalidItemList, fail)
    return render(request, 'item_monitor_week.html',{"avalidItemLi": avalidItemLi, "total_data": total_data,
                                                     "avalidItemList":avalidItemList})



#错误url同步
def synfailurl(request):
    if request.method == "GET":
        failUrlList = Fail_url_detail.objects.filter(status_code="404")
        pass

def updateUrl(request):
    if request.method == "POST":
        pass