# -*- coding:utf-8 -*-
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import redis
import json
from .lplush import SpiderListUrl
import zzh.conf
import time
from .utils import scrapyd_url
from scrapyd_api import ScrapydAPI
from requests.exceptions import ConnectionError

import logging
from .models import Node, Project, Deploy, Monitor,Spider,Scheduler
from .response import JsonResponse
logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)
schedulerd = BackgroundScheduler()


def task(request,project_name,spider_names,client_id):
    client = Node.objects.get(id=client_id)
    scrapyd = ScrapydAPI(scrapyd_url(client.ip,client.port))
    try:
        for spider_name in spider_names:
            task = scrapyd.schedule(project_name,spider_name)
            return JsonResponse(task)
    except ConnectionError:
        return JsonResponse({'message':'Connect Error'},status=500)


def schedulerTask(request,task,scheduler_id):
    if request.method == "POST":
        spider = Scheduler.objects.filter(id=scheduler_id)
        print(spider)
        spider_time = 10
        #spider_url = Scheduler.objects.filter(scheduler_id=scheduler_id).get()
        schedulerd.add_job(task, 'interval', minutes=10)
        #scheduler.add_job(lupush, 'interval', minute="%s" % spider_url)
        # print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
        try:
            while True:
                schedulerd.start()
                time.sleep(2)
        except (KeyboardInterrupt, SystemExit):
            schedulerd.shutdown()
            schedulerd.start()


#移除调度作业
def remove_scheduler(request,schedule_id):
    if request.method == 'POST':
        # if db.jobs.findOne():
        schedulerd.remove_job(schedule_id)

# scheduler.add_job(myfunc, 'interval', minutes=2, id='my_job_id')
# scheduler.remove_job('my_job_id')

#暂停调度
def schedulerStopTask():
    schedulerd.pause()


#恢复调度


def schedulerResumeTask():
    schedulerd.resume()


#关闭调度
def closeScheduler():
    schedulerd.shutdown()
    #默认情况下调度器会等待所有正在运行的作业完成后，关闭所有的调度器和作业存储。如果你不想等待，可以将wait选项设置为False。
    schedulerd.shutdown(wait=False)


