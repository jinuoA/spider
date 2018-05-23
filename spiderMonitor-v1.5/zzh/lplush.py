# coding=utf-8
import redis
import json
import zzh.conf
import os
from django.http import HttpResponse
from os.path import join
from .utils import IGNORES
from cmd.init import PROJECTS_FOLDER
import requests
from requests.exceptions import ConnectionError
from scrapyd_api import ScrapydAPI
from .models import  Project, Deploy, Monitor,Spider,Scheduler,Node,ProjectRuler
from .response import JsonResponse
from django.forms.models import model_to_dict
from .utils import scrapyd_url,log_url
data_list = [{
                "spider": "basescrawler:rules",
                "project": "zzh",
                "srcapy_type": "",
                "dept_id": "1",
                "list_xpath": "/html/body/div/div[2]/div[1]/div/div[2]/ul/li",
                "title_xpath": "a/text()",
                "pdate_xpath": "",
                "url_xpath": "a/@href",
                "expiration_date": 30,
                "next_page": "//a[text()='下一页']/@href",
                "url": "http://www.pujiang.gov.cn/index.php?cid=2400"
            },
            {
                "spider": "basescrawler:rules",
                "project": "zzh",
                "srcapy_type": "",
                "dept_id": "1",
                "list_xpath": "//div[@class='xw0bac']/ul/li",
                "title_xpath": "a/@title",
                "pdate_xpath": "",
                "url_xpath": "a/@href",
                "expiration_date": 30,
                "next_page": "//a[text()='下一页']/@href",
                "url": "http://www.yajxw.gov.cn/articlist.htm?id=20170527085102550"
            }

]



def create_ruler(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        dataList = Spider.objects.create(**data)
        return JsonResponse(model_to_dict(dataList))

def ruler_remove(request, ruler_id):

    if request.method == 'POST':
        Spider.objects.filter(id=ruler_id).delete()
        return JsonResponse({'result': '1'})


def ruler_update(request, ruler_id):

    if request.method == 'POST':
        spider = Spider.objects.filter(id=ruler_id)
        data = json.loads(request.body.decode('utf-8'))
        spider.update(**data)
        return JsonResponse(model_to_dict(Spider.objects.get(id=ruler_id)))


def create_scheduler(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        dataList = Scheduler.objects.create(**data)
        return JsonResponse(model_to_dict(dataList))


def scheduler_update(request,scheduler_id):
    if request.method == 'POST':
        scheder = Scheduler.objects.filter(id=scheduler_id)
        data = json.loads(request.body.decode('utf-8'))
        scheder.update(**data)
        return JsonResponse(model_to_dict(Scheduler.objects.get(id=scheduler_id)))


def scheduler_remove(request,scheduler_id):
    if request.method == 'POST':
        Scheduler.objects.filter(id=scheduler_id).delete()
        return JsonResponse({'result':'1'})

def job_log(request, node_id, project_name, spider_name, job_id):
    if request.method == 'GET':
        node = Node.objects.get(id=node_id)
        # get log url
        url = log_url(node.ip, node.port, project_name, spider_name, job_id)
        try:
            # get last 1000 bytes of log
            response = requests.get(url)
            response.encoding = response.apparent_encoding
            # log not found
            if response.status_code == 404:
                return JsonResponse({'message': 'Log Not Found'}, status=404)
            text = response.text
            return HttpResponse(text)
        except requests.ConnectionError:
            return JsonResponse({'message': 'Load Log Error'}, status=500)


#撤销部署爬虫
def remove_depody_spider(request,client_id,project,version_name):
    if request.method == 'POST':
        client = Node.objects.get(id=client_id)
        scrapyd = ScrapydAPI(scrapyd_url(client.ip,client.port))
        try:
            spider = scrapyd.delete_version(project,version_name)
            return JsonResponse(spider)
        except ConnectionError:
            return JsonResponse({'message':'Connect Error'}, status=500)


def remove_all_version(request,project,client_id):
    client = Node.objects.get(id=client_id)
    scrapyd = ScrapydAPI(scrapyd_url(client.ip,client.port))
    try:
        versions = scrapyd.delete_project(project)
        return JsonResponse(versions)
    except ConnectionError:
        return JsonResponse({'message':'Connet Error'},status=500)


#获取发布爬虫列表
def get_spider_version(request,project,client_id):
    client = Node.objects.get(id=client_id)
    scrapyd = ScrapydAPI(scrapyd_url(client.ip,client.port))
    try:
        spiders = scrapyd.list_spiders(project)
        spiders = [{'name': spider, 'id': index + 1} for index, spider in enumerate(spiders)]
        return JsonResponse(spiders)
    except ConnectionError:
        return JsonResponse({'message': 'Connect Error'}, status=500)


#获取项目已发布爬虫版本
def get_project_version(request,project,client_id):
    if request.method == 'GET':
        client = Node.objects.get(id=client_id)
        scrapyd = ScrapydAPI(scrapyd_url(client.ip,client.port))
        try:
            versions = scrapyd.list_versions(project)
            versions = [{'name': version, 'id': index + 1} for index, version in enumerate(versions)]
            return JsonResponse(versions)
        except ConnectionError:
            return JsonResponse({'message': 'Connect Error'}, status=500)


def project_index(request):
    """
    project index list
    :param request: request object
    :return: json
    """
    if request.method == 'GET':
        path = os.path.abspath(join(os.getcwd(), PROJECTS_FOLDER))
        files = os.listdir(path)
        project_list = []
        for file in files:
            if os.path.isdir(join(path, file)) and not file in IGNORES:
                project_list.append({'name': file})
        print(project_list)
        return JsonResponse(project_list)






# 4、获取项目下已发布的爬虫版本列表
# http://127.0.0.1:6800/listversions.json?project=myproject
# 7、删除某一版本爬虫
# http: // 127.0.0.1:6800 / delversion.json
# （post方式，data = {"project": myproject, "version": myversion}）
# 8、删除某一工程，包括该工程下的各版本爬虫
# http: // 127.0.0.1:6800 / delproject.json（post方式，data = {"project": myproject}）
#



def SpiderListUrl(request,scheduler_id):
    if request.method == 'GET':
        # data_list = Spider.objects.all()
        data_list = ProjectRuler.objects.filter(scheduler_id=scheduler_id)
        for data in data_list:
            # 将字典编码为json字符串
            reminder_str = json.dumps(data)
            # 连接redis并将数据插入redis中
            r = redis.StrictRedis(host=conf.redisHost, port=conf.redisPort, db=0)
            print(r.lpush('basescrawler:rules', reminder_str))



                    # def SpiderList(request):
#     if request.method == 'GET':
#         data_list = Spider.objects.all()
#         for data in data_list:
#             # 将字典编码为json字符串
#             reminder_str = json.dumps(data)
#
#             # 连接redis并将数据插入redis中
#             r = redis.StrictRedis(host=conf.redisHost, port=conf.redisPort, db=0)
#             print r.lpush('basescrawler:rules', reminder_str)
#
#             # 如果所有数据已入队
#             # 可以在最后插入一个空数据作为结束的标志
#             #r.lpush('test_list', '{}')




# 7、删除某一版本爬虫
# http://127.0.0.1:6800/delversion.json
# （post方式，data={"project":myproject,"version":myversion}）