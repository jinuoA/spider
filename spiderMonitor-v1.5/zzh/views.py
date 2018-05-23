# -*-coding:utf-8 -*-
import json, os, requests, time, pytz, pymongo, string
from shutil import move, copy, rmtree
from scrapyd_api import ScrapydAPI
from requests.exceptions import ConnectionError
from os.path import join, exists
from django.shortcuts import render
from django.core.serializers import serialize
from django.http import HttpResponse
from django.forms.models import model_to_dict
from django.utils import timezone
from zzh.response import JsonResponse
from cmd.init import PROJECTS_FOLDER
from spiderMonitor.settings import TIME_ZONE
from .models import Project, Deploy, Monitor, Spider, Scheduler, ProjectRuler, Node,Fail_url_detail,Item_monitor,Queue_url_monitor,Spider_url_monitor, \
    SpiderTemplates,Task,Task_url,Invalid_task_url
from .build import build_project, find_egg
from .utils import IGNORES, is_valid_name, copy_tree, TEMPLATES_DIR, TEMPLATES_TO_RENDER, \
    render_template, get_traceback, scrapyd_url, log_url, get_tree
from apscheduler.schedulers.background import BackgroundScheduler
from .APScheduler import schedulerTask
from .lplush import SpiderListUrl
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger
import redis
from zzh import config
from django.db.models import F
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse,HttpResponseRedirect
from django.db.models import Q
from django.http import HttpResponse
from xlwt import *
from io import StringIO,BytesIO
from datetime import timedelta,date
import logging
import time
import re
import datetime
# from zzh import start_schedler
from zzh import schedul
from zzh.page import pageT



class CJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)



def index(request):
    """
    render index page
    :param request: request object
    :return: page
    """
    # return render(request,'index.html',{'result':1})
    return render(request,'index.html')

def index_status(request):
    """
    index statistics
    :param request: request object
    :return: json
    """
    if request.method == 'GET':
        nodes = Node.objects.all()
        data = {
            'success': 0,
            'error': 0,
            'project': 0,
        }
        # nodes info
        for node in nodes:
            try:
                requests.get(scrapyd_url(node.node_ip, node.node_port), timeout=1)
                data['success'] += 1
            except ConnectionError:
                data['error'] += 1
        path = os.path.abspath(join(os.getcwd(), PROJECTS_FOLDER))
        files = os.listdir(path)
        # projects info
        for file in files:
            if os.path.isdir(join(path, file)) and not file in IGNORES:
                data['project'] += 1
        return JsonResponse(data)


def node_index(request):
    """
    get node list
    :param request: request object
    :return: node list
    """
    data = Node.objects.order_by('-id').values('node_name', 'id', 'node_port', 'node_ip', 'node_status')
    data = json.dumps(list(data))
    return HttpResponse(data)
    # data = serialize('json', Node.objects.order_by('-id'),fields=('node_name','id','node_port','node_ip','node_status'))
    # data = [x['fields'] for x in data]
    # return HttpResponse(data)
    # return HttpResponse(serialize("json", Node.objects.order_by('-id').values('node_name','id','node_port','node_ip','node_status')))


def node_info(request, node_id):
    """
    get node info
    :param request: request object
    :param id: node id
    :return: json
    """
    if request.method == 'GET':
        return JsonResponse(model_to_dict(Node.objects.get(id=node_id)))


def node_status(request, node_id):
    """
    get node status
    :param request: request object
    :param node_id: node id
    :return: json
    """
    if request.method == 'GET':
        # get node object
        node = Node.objects.get(id=node_id)
        try:
            requests.get(scrapyd_url(node.node_ip, node.node_port), timeout=3)
            return JsonResponse({'result': '1'})
        except ConnectionError:
            return JsonResponse({'message': 'Connect Error'}, status=500)


def node_update(request, node_id):
    """
    update node info
    :param request: request object
    :param node_id: node id
    :return: json
    """
    if request.method == 'POST':
        node = Node.objects.filter(id=node_id)
        data = json.loads(request.body.decode('utf-8'))
        node.update(**data)
        return JsonResponse(model_to_dict(Node.objects.get(id=node_id)))


def node_create(request):
    """
    create a node
    :param request: request object
    :return: json
    """

    if request.method == 'POST':
        print(request.body)
        data = json.loads(request.body.decode('utf-8'))
        node = Node.objects.create(**data)
        return JsonResponse(model_to_dict(node))


def node_remove(request, node_id):
    """
    remove a node
    :param request: request object
    :param node_id: node id
    :return: json
    """
    if request.method == 'POST':
        Node.objects.filter(id=node_id).delete()
        return JsonResponse({'result': '1'})


def spider_list(request, node_id, spider_name):
    """
    get spider list from one node
    :param request: request Object
    :param node_id: node id
    :param project_name: project name
    :return: json
    """
    if request.method == 'GET':
        node = Node.objects.get(id=node_id)
        scrapyd = ScrapydAPI(scrapyd_url(node.node_ip, node.node_port))
        try:
            spiders = scrapyd.list_spiders(spider_name)
            spiders = [{'name': spider, 'id': index + 1} for index, spider in enumerate(spiders)]
            return JsonResponse({"result":1,"spiders":spiders})
        except ConnectionError:
            return JsonResponse({'message': 'Connect Error'}, status=500)


def spider_start(request, node_id, project_name, spider_name):
    """
    start a spider
    :param request: request object
    :param node_id: node id
    :param project_name: project name
    :param spider_name: spider name
    :return: json
    """
    if request.method == 'GET':
        node = Node.objects.get(id=node_id)
        scrapyd = ScrapydAPI(scrapyd_url(node.node_ip, node.node_port))
        try:
            job = scrapyd.schedule(project_name, spider_name)
            return JsonResponse({'job': job,"result":1})
        except ConnectionError:
            return JsonResponse({'message': 'Connect Error'}, status=500)


def spider_start_time(request, node_id, project_name, spider_name, schedule_id):
    def task():
        node = Node.objects.get(id=node_id)
        scrapyd = ScrapydAPI(scrapyd_url(node.node_ip, node.node_port))
        try:
            job = scrapyd.schedule(project_name, spider_name)
            return JsonResponse({'job': job})
        except ConnectionError:
            return JsonResponse({'message': 'Connect Error'}, status=500)

    if request.method == 'GET':
        schedulerTask(request, task, SpiderListUrl, schedule_id)



def project_list(request, node_id):
    """
    project deployed list on one node
    :param request: request object
    :param node_id: node id
    :return: json
    """
    if request.method == 'GET':
        node = Node.objects.get(id=node_id)
        scrapyd = ScrapydAPI(scrapyd_url(node.node_ip, node.node_port))
        try:
            projects = scrapyd.list_projects()
            lis = []
            for project in projects:
                lis.append({'spider_name':project})
            return JsonResponse({'result':1,'lis':lis})
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


def project_configure(request, project_name):
    """
    get or update configuration
    :param request: request object
    :param project_name: project name
    :return: json
    """
    # get configuration
    if request.method == 'GET':
        project = Project.objects.get(name=project_name)
        project = model_to_dict(project)
        project['configuration'] = json.loads(project['configuration']) if project['configuration'] else None
        return JsonResponse(project)
    # update configuration
    elif request.method == 'POST':
        project = Project.objects.filter(name=project_name)
        data = json.loads(request.body.decode('utf-8'))
        configuration = json.dumps(data.get('configuration'))
        project.update(**{'configuration': configuration})
        project = Project.objects.get(name=project_name)
        project = model_to_dict(project)
        return JsonResponse(project)


def project_tree(request, project_name):
    """
    get file tree of project
    :param request: request object
    :param project_name: project name
    :return: json of tree
    """
    if request.method == 'GET':
        path = os.path.abspath(join(os.getcwd(), PROJECTS_FOLDER))
        # get tree data
        tree = get_tree(join(path, project_name))
        return JsonResponse(tree)


def project_create(request):
    """
    create a configurable project
    :param request: request object
    :return: json
    """
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        data['configurable'] = 1
        project, result = Project.objects.update_or_create(**data)
        # generate a single project folder
        path = join(os.path.abspath(join(os.getcwd(), PROJECTS_FOLDER)), data['spider_name'])
        os.mkdir(path)
        return JsonResponse(model_to_dict(project))


def project_remove(request, spider_name):
    """
    remove project from disk and db
    :param request: request object
    :param project_name: project name
    :return: result of remove
    """
    if request.method == 'POST':
        path = join(os.path.abspath(os.getcwd()), PROJECTS_FOLDER)
        project_path = join(path, spider_name)
        if not project_path:
        # delete project file tree
            rmtree(project_path)
            # delete project
            result = Project.objects.filter(spider_name=spider_name).delete()
            return JsonResponse({'result': result})
        else:
            rmtree(project_path)
            result = Project.objects.filter(spider_name=spider_name).delete()
            return JsonResponse({'result': result})


def project_update(request, spider_name):
    """
    update node info
    :param request: request object
    :param node_id: node id
    :return: json
    """
    if request.method == 'POST':
        path = join(os.path.abspath(os.getcwd()), PROJECTS_FOLDER)
        project_path = join(path, spider_name)
        if not project_path:
        # delete project file tree
            rmtree(project_path)
            project = Project.objects.filter(spider_name=spider_name)
            data = json.loads(request.body.decode('utf-8'))
            project.update(**data)
            return JsonResponse(model_to_dict(Project.objects.get(spider_name=spider_name)))
        else:
            project = Project.objects.filter(spider_name=spider_name)
            data = json.loads(request.body.decode('utf-8'))
            project.update(**data)
            return JsonResponse(model_to_dict(Project.objects.get(spider_name=spider_name)))



def project_version(request, node_id, project_name):
    """
    get project deploy version
    :param request: request object
    :param node_id: node id
    :param project_name: project name
    :return: deploy version of project
    """
    if request.method == 'GET':
        # get node and project model
        node = Node.objects.get(id=node_id)
        project = Project.objects.get(name=project_name)
        scrapyd = ScrapydAPI(scrapyd_url(node.node_ip, node.node_port))
        # if deploy info exists in db, return it
        if Deploy.objects.filter(node=node, project=project):
            deploy = Deploy.objects.get(node=node, project=project)
        # if deploy info does not exists in db, create deploy info
        else:
            try:
                versions = scrapyd.list_versions(project_name)
            except ConnectionError:
                return JsonResponse({'message': 'Connect Error'}, status=500)
            if len(versions) > 0:
                version = versions[-1]
                deployed_at = timezone.datetime.fromtimestamp(int(version), tz=pytz.timezone(TIME_ZONE))
            else:
                deployed_at = None
            deploy, result = Deploy.objects.update_or_create(node=node, project=project, deployed_at=deployed_at)
        # return deploy json info
        return JsonResponse(model_to_dict(deploy))


def project_build(request, project_name):
    """
    get build info or execute build operation
    :param request: request object
    :param project_name: project name
    :return: json
    """
    # get project folder
    path = os.path.abspath(join(os.getcwd(), PROJECTS_FOLDER))
    project_path = join(path, project_name)
    # get build version
    if request.method == 'GET':
        egg = find_egg(project_path)
        # if built, save or update project to db
        if egg:
            built_at = timezone.datetime.fromtimestamp(os.path.getmtime(join(project_path, egg)),
                                                       tz=pytz.timezone(TIME_ZONE))
            if not Project.objects.filter(spider_name=project_name):
                Project(spider_name=project_name, built_at=built_at, egg=egg).save()
                model = Project.objects.get(spider_name=project_name)
            else:
                model = Project.objects.get(spider_name=project_name)
                model.built_at = built_at
                model.egg = egg
                model.save()

        else:  # if not built, just save project name to db
            if not Project.objects.filter(spider_name=project_name):
                Project(name=project_name).save()
            model = Project.objects.get(spider_name=project_name)
        # transfer model to dict then dumps it to json
        data = model_to_dict(model)
        return JsonResponse(data)
    # build operation manually by clicking button
    elif request.method == 'POST':
        # data = json.loads(request.body.decode('utf-8'))
        # description = data['spider_desc']
        build_project(project_name)
        egg = find_egg(project_path)
        # update built_at info
        built_at = timezone.now()
        # if project does not exists in db, create it
        if not Project.objects.filter(spider_name=project_name):
            Project(name=project_name, description=Project.spider_desc, built_at=built_at, egg=egg).save()
            model = Project.objects.get(spider_name=project_name)
        # if project exists, update egg, description, built_at info
        else:
            model = Project.objects.get(spider_name=project_name)
            model.built_at = built_at
            model.egg = egg
            # model.description = description
            model.save()
        # transfer model to dict then dumps it to json
        # data = model_to_dict(model)
        return JsonResponse({"result": 1})


def project_deploy(request, node_id, project_name):
    if request.method == 'POST':
        # get project folder
        path = os.path.abspath(join(os.getcwd(), PROJECTS_FOLDER))
        project_path = join(path, project_name)
        # find egg file
        egg = find_egg(project_path)
        egg_file = open(join(project_path, egg), 'rb')
        # get node and project model
        node = Node.objects.get(id=node_id)
        project = Project.objects.get(spider_name=project_name)
        # execute deploy operation
        scrapyd = ScrapydAPI(scrapyd_url(node.node_ip, node.node_port))
        try:
            scrapyd.add_version(project_name, int(time.time()), egg_file.read())
            # update deploy info
            deployed_at = datetime.datetime.now()
            deployed_at = deployed_at.strftime("%Y-%m-%d %H:%M:%S")
            Deploy.objects.filter(node=node, project=project).delete()
            deploy, result = Deploy.objects.update_or_create(node=node, project=project, deployed_at=deployed_at,
                                                             description=project.spider_desc)
            return JsonResponse({'result': 1, "deploy": model_to_dict(deploy)})
        except Exception:
            return JsonResponse({'message': get_traceback()}, status=500)


def project_generate(request, project_name):
    """
    generate code of project
    :param request: request object
    :param project_name: project name
    :return: json of generated project
    """
    if request.method == 'POST':
        # get configuration
        configuration = Project.objects.get(name=project_name).configuration
        configuration = json.loads(configuration)

        if not is_valid_name(project_name):
            return JsonResponse({'message': 'Invalid project name'}, status=500)
        # remove original project dir
        project_dir = join(PROJECTS_FOLDER, project_name)
        if exists(project_dir):
            rmtree(project_dir)
        # generate project
        copy_tree(join(TEMPLATES_DIR, 'project'), project_dir)
        move(join(PROJECTS_FOLDER, project_name, 'module'), join(project_dir, project_name))
        for paths in TEMPLATES_TO_RENDER:
            path = join(*paths)
            tplfile = join(project_dir,
                           string.Template(path).substitute(project_name=project_name))
            vars = {
                'project_name': project_name,
                'items': configuration.get('items'),
            }
            render_template(tplfile, tplfile.rstrip('.tmpl'), **vars)
        # generate spider
        spiders = configuration.get('spiders')
        for spider in spiders:
            source_tpl_file = join(TEMPLATES_DIR, 'spiders', 'crawl.tmpl')
            new_tpl_file = join(PROJECTS_FOLDER, project_name, project_name, 'spiders', 'crawl.tmpl')
            spider_file = "%s.py" % join(PROJECTS_FOLDER, project_name, project_name, 'spiders', spider.get('name'))
            copy(source_tpl_file, new_tpl_file)
            render_template(new_tpl_file, spider_file, spider=spider, project_name=project_name)
        # save generated_at attr
        model = Project.objects.get(name=project_name)
        model.generated_at = timezone.now()
        # clear built_at attr
        model.built_at = None
        model.save()
        # return model
        return JsonResponse(model_to_dict(model))


def project_file_read(request):
    """
    get content of project file
    :param request: request object
    :return: file content
    """
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        path = join(data['path'], data['label'])
        with open(path, 'r') as f:
            return HttpResponse(f.read())


def project_file_update(request):
    """
    update project file
    :param request: request object
    :return: result of update
    """
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        path = join(data['path'], data['label'])
        code = data['code']
        with open(path, 'w') as f:
            f.write(code)
            return JsonResponse({'result': '1'})


def project_file_create(request):
    """
    create project file
    :param request: request object
    :return: result of create
    """
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        path = join(data['path'], data['name'])
        open(path, 'w').close()
        return JsonResponse({'result': '1'})


def project_file_delete(request):
    """
    delete project file
    :param request: request object
    :return: result of delete
    """
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        path = join(data['path'], data['label'])
        result = os.remove(path)
        return JsonResponse({'result': result})


def project_file_rename(request):
    """
    rename file name
    :param request: request object
    :return: result of rename
    """
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        pre = join(data['path'], data['pre'])
        new = join(data['path'], data['new'])
        os.rename(pre, new)
        return JsonResponse({'result': '1'})


def job_list(request, node_id, project_name):
    """
    get job list of project from one node
    :param request: request object
    :param node_id: node id
    :param project_name: project name
    :return: list of jobs
    """
    if request.method == 'GET':
        node = Node.objects.get(id=node_id)
        scrapyd = ScrapydAPI(scrapyd_url(node.node_ip, node.node_port))
        try:
            result = scrapyd.list_jobs(project_name)
            jobs = []
            statuses = ['pending', 'running', 'finished']
            for status in statuses:
                for job in result.get(status):
                    job['status'] = status
                    jobs.append(job)
            return JsonResponse({"result":1,"jobs":jobs})
        except ConnectionError:
            return JsonResponse({'message': 'Connect Error'}, status=500)


def job_log(request, client_id, project_name, spider_name, job_id):
    """
    get log of jog
    :param request: request object
    :param client_id: client id
    :param project_name: project name
    :param spider_name: spider name
    :param job_id: job id
    :return: log of job
    """
    if request.method == 'GET':
        node = Node.objects.get(id=client_id)
        # get log url
        url = log_url(node.ip, node.port, project_name, spider_name, job_id)
        try:
            # get last 1000 bytes of log
            response = requests.get(url, timeout=5, headers={
                'Range': 'bytes=-1000'
            }, auth=(node.username, node.password) if node.auth else None)
            # Get encoding
            encoding = response.apparent_encoding
            # log not found
            if response.status_code == 404:
                return JsonResponse({'message': 'Log Not Found'}, status=404)
            # bytes to string
            text = response.content.decode(encoding, errors='replace')
            return HttpResponse(text)
        except requests.ConnectionError:
            return JsonResponse({'message': 'Load Log Error'}, status=500)


def job_cancel(request, node_id, project_name, job_id):
    """
    cancel a job
    :param request: request object
    :param node_id: node id
    :param project_name: project name
    :param job_id: job id
    :return: json of cancel
    """
    if request.method == 'GET':
        node = Node.objects.get(id=node_id)
        try:
            scrapyd = ScrapydAPI(scrapyd_url(node.node_ip, node.node_port))
            res = scrapyd.cancel(project_name, job_id)
            return JsonResponse({"res":res,"result":1})
        except ConnectionError:
            return JsonResponse({'message': 'Connect Error'})


def monitor_db_list(request):
    """
    get monitor db list
    :param request: request object
    :return: json of db list
    """
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        url = data['url']
        type = data['type']
        if type == 'MongoDB':
            node = pymongo.Mongonode(url)
            dbs = node.database_names()
            return JsonResponse(dbs)


def monitor_collection_list(request):
    """
    get monitor collection list
    :param request: request object
    :return: json of collection list
    """
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        url = data['url']
        db = data['db']
        type = data['type']
        if type == 'MongoDB':
            node = pymongo.Mongonode(url)
            db = node[db]
            collections = db.collection_names()
            return JsonResponse(collections)


def monitor_create(request):
    """
    create a monitor
    :param request: request object
    :return: json of create
    """
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        data = data['form']
        data['configuration'] = json.dumps(data['configuration'])
        monitor = Monitor.objects.create(**data)
        return JsonResponse(model_to_dict(monitor))


def create_ruler(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        dataList = ProjectRuler.objects.create(**data)
        return JsonResponse(model_to_dict(dataList))


def ruler_remove(request, ruler_id):
    if request.method == 'POST':
        ProjectRuler.objects.filter(id=ruler_id).delete()
        return JsonResponse({'result': '1'})


def ruler_update(request, ruler_id):
    if request.method == 'POST':
        spider = ProjectRuler.objects.filter(id=ruler_id)
        data = json.loads(request.body.decode('utf-8'))
        spider.update(**data)
        return JsonResponse(model_to_dict(ProjectRuler.objects.get(id=ruler_id)))


def create_scheduler(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        dataList = Scheduler.objects.create(**data)
        return JsonResponse(model_to_dict(dataList))


def scheduler_update(request, scheduler_id):
    if request.method == 'POST':
        scheder = Scheduler.objects.filter(id=scheduler_id)
        data = json.loads(request.body.decode('utf-8'))
        scheder.update(**data)
        return JsonResponse(model_to_dict(Scheduler.objects.get(id=scheduler_id)))


def scheduler_remove(request, scheduler_id):
    if request.method == 'POST':
        Scheduler.objects.filter(id=scheduler_id).delete()
        return JsonResponse({'result': '1'})


def scheduler_index(request):
    """
    get node list
    :param request: request object
    :return: node list
    """

    data = Scheduler.objects.order_by('-id').values()
    data = json.dumps(list(data), cls=CJsonEncoder)
    return HttpResponse(data)

    # return JsonResponse([dict(x["fields"],**{"id":x["pk"]})for x in json.loads(Scheduler.objects.order_by('-id'))])


def scheduler_run(request, project_name, spider_names, node_id, schedule_id):
    def task():
        node = Node.objects.get(id=node_id)
        scrapyd = ScrapydAPI(scrapyd_url(node.node_ip, node.node_port))
        try:
            for spider_name in spider_names:
                task = scrapyd.schedule(project_name, spider_name)
                return JsonResponse(task)
        except ConnectionError:
            return JsonResponse({'message': 'Connect Error'}, status=500)

    schedulerTask(request, task,schedule_id)


def ruler_index(request):
    """
    get project list
    :param request: request object
    :return: node list
    """
    if request.method == "GET":
        PR = ProjectRuler.objects.select_related('scheduler','project').filter(dept_name_key__istartswith="50",is_lock=1)
        lis = []
        for p in PR:
            if p.project != None:
                project_name = p.project.spider_name
            else:
                project_name = "未部署"
            if p.scheduler != None:
                schduler_name = p.scheduler.schedule_name
            else:
                schduler_name = "未添加调度"
            id = p.id
            project_desc = p.project_desc
            dept_id = p.dept_id
            url = p.url
            data={
            "id":id,
            "schduler_name":schduler_name,
            "spider_name" :project_name,
            "project_desc":project_desc,
            "dept_id" :dept_id,
            "url" :url,
            }
            lis.append(data)
        return JsonResponse(lis)


def ruler_indexs(request):
    """
    get project list
    :param request: request object
    :return: node list
    """
    if request.method == "GET":
        PR = ProjectRuler.objects.select_related('scheduler','project').filter(is_lock=1)
        lis = []
        for p in PR:
            if p.project != None:
                project_name = p.project.spider_name
            else:
                project_name = "未部署"
            if p.scheduler != None:
                schduler_name = p.scheduler.schedule_name
            else:
                schduler_name = "未添加调度"
            id = p.id
            project_desc = p.project_desc
            dept_id = p.dept_id
            url = p.url
            data={
            "id":id,
            "schduler_name":schduler_name,
            "spider_name" :project_name,
            "project_desc":project_desc,
            "dept_id" :dept_id,
            "url" :url,
            }
            lis.append(data)
        return JsonResponse(lis)


def ruler_name(request):
    spider_name = ProjectRuler.objects.model.project_name
    for i in spider_name:
        print(i)
    # print(spider_name)
    return JsonResponse({'result':1})


def spider_index(request):
    """
    get node list
    :param request: request object
    :return: node list
    """
    data = Project.objects.order_by('-id').values()
    data = json.dumps(list(data), cls=CJsonEncoder)
    return HttpResponse(data)
    # return HttpResponse(serialize('json', Project.objects.order_by('-id')))


def paginator(request,obje):
    if request.method == "POST":
        contact_list = eval(obje).objects.all().order_by('id')
        data = json.loads(request.body.decode('utf-8'))
        page = data['page']
        page_num = data['page_num']

        paginator = Paginator(contact_list, page_num)  # Show 25 contacts per page
        try:
            contacts = paginator.page(page)
            contacts = [dict(x["fields"], **{"id": x["pk"]}) for x in json.loads((serialize("json", contacts)))]
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            contacts = paginator.page(1)
            contacts = [dict(x["fields"], **{"id": x["pk"]}) for x in json.loads((serialize("json", contacts)))]
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            contacts = paginator.page(paginator.num_pages)
            contacts = [dict(x["fields"], **{"id": x["pk"]}) for x in json.loads((serialize("json", contacts)))]
        return JsonResponse(contacts)


def scheduler_run_ruler_new(request, scheduler_id):
    scheduler = BackgroundScheduler()

    def SpiderListUrl():
        if request.method == 'GET':
            # data_list = Spider.objects.all()
            schedule = Scheduler.objects.get(id=scheduler_id)
            # redis_ip = schedule.scrapyd_ip
            # redis_port = schedule.scrapyd_port
            data_list = ProjectRuler.objects.filter(scheduler_id=scheduler_id).values()
            data_list = json.dumps(list(data_list), cls=CJsonEncoder)
            data_list = json.loads(data_list)
            for data in data_list:
                # 将字典编码为json字符串
                reminder_str = json.dumps(data)
                # 连接redis并将数据插入redis中
                r = redis.StrictRedis(host=config.redisHost, port=config.redisPort, db=0)
                # r = redis.StrictRedis(host=redis_ip, port=redis_port, db=0)
                print(r.lpush('basescrawler:rules', reminder_str))
            return JsonResponse(data_list)
    if request.method == "GET":
        schedule = Scheduler.objects.get(id=scheduler_id)
        spider_time = schedule.spider_time
        print(spider_time)
        scheduler.add_job(SpiderListUrl, 'interval', minutes=spider_time,id='my_scheduler_job')
        try:
            while True:
                scheduler.start()
                time.sleep(2)
                return JsonResponse({'result': 1})
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
            scheduler.start()


def add_project(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        ids = data['ids']
        spider_id = data['spider_id']
        for id in ids:
            spider = ProjectRuler.objects.filter(id=id,is_lock=1)
            spider.update(project_id=spider_id)
        return JsonResponse({'result': 1})


def delete_project(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        ids = data['ids']
        spider_id = data['spider_id']
        for id in ids:
            spider = ProjectRuler.objects.filter(id=id)
            spider.update(project_id=None)
        return JsonResponse({'result': 1})


def add_spider_scheduler(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        ids = data['ids']
        scheduler_id = data['scheduler_id']       # scheduler_id = data['scheduler_id']    //修改成 enabled   值为0表示不定时，1定时
        spider = ProjectRuler.objects.filter(id(ids))
        spider.update(Scheduler_id=scheduler_id)
        return JsonResponse({'result': 1})


def delete_spider_scheduler(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        ids = data['ids']
        spider = ProjectRuler.objects.filter(id(ids))
        spider.update(Scheduler_id=None)
        return JsonResponse({'result': 1})


def checked_project(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        ids = data['ids']
        ls = []
        for id in ids:
            data = ProjectRuler.objects.filter(id=id).values()
            data = json.dumps(list(data), cls=CJsonEncoder)
            ls.append(data)
        return HttpResponse(ls)


def checked_spider(request):
    """
    :param request:
    :return:
    """
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        ids = data['ids']
        ls = []
        for id in ids:
            data = Project.objects.filter(id=id).values()
            data = json.dumps(list(data), cls=CJsonEncoder)
            ls.append(data)
        return HttpResponse(ls)


def added_project(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        spider_id = data['spider_id']
        project_list = json.dumps(list(ProjectRuler.objects.filter(project_id=spider_id).values()), cls=CJsonEncoder)
        return HttpResponse(project_list)


def added_spiders(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        scheduler_id = data['scheduler_id']
        spider_list = json.dumps(list(Project.objects.filter(Scheduler_id=scheduler_id).values()),
                                 cls=CJsonEncoder)
        return HttpResponse(spider_list)


# 撤销部署爬虫
def remove_depody_spider(request, client_id, project, version_name):
    if request.method == 'POST':
        node = Node.objects.get(id=client_id)
        scrapyd = ScrapydAPI(scrapyd_url(node.node_ip, node.node_port))
        try:
            spider = scrapyd.delete_version(project, version_name)
            return JsonResponse(spider)
        except ConnectionError:
            return JsonResponse({'message': 'Connect Error'}, status=500)


def remove_all_version(request, project, client_id):
    node = Node.objects.get(id=client_id)
    scrapyd = ScrapydAPI(scrapyd_url(node.node_ip, node.node_port))
    try:
        versions = scrapyd.delete_project(project)
        return JsonResponse(versions)
    except ConnectionError:
        return JsonResponse({'message': 'Connet Error'}, status=500)


# 获取发布爬虫列表
def get_spider_version(request, project, client_id):
    node = Node.objects.get(id=client_id)
    scrapyd = ScrapydAPI(scrapyd_url(node.node_ip, node.node_port))
    try:
        spiders = scrapyd.list_spiders(project)
        spiders = [{'name': spider, 'id': index + 1} for index, spider in enumerate(spiders)]
        return JsonResponse(spiders)
    except ConnectionError:
        return JsonResponse({'message': 'Connect Error'}, status=500)


# 获取项目已发布爬虫版本
def get_project_version(request, project, node_id):
    if request.method == 'GET':
        print('ssss')
        node = Node.objects.get(id=node_id)
        scrapyd = ScrapydAPI(scrapyd_url(node.node_ip, node.node_port))
        try:
            versions = scrapyd.list_versions(project)
            versions = [{'name': version, 'id': index + 1} for index, version in enumerate(versions)]
            return JsonResponse(versions)
        except ConnectionError:
            return JsonResponse({'message': 'Connect Error'}, status=500)


def update_status(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        model = data['model']
        is_lock = data['isLock']
        ids = data['ids']
        for id in ids:
            spider = eval(model).objects.filter(id=id)
            if model == 'ProjectRuler' and is_lock == 0:
                spider.update(is_lock=is_lock,scheduler_id=None)
            if model == 'ProjectRuler' and is_lock == 1:
                spider.update(is_lock=is_lock,scheduler_id=1)
            else:
                spider.update(is_lock=is_lock)
        return JsonResponse({'result': 1})


def spider_template(request, ruler_id):
    if request.method == 'POST':
        spider = ProjectRuler.objects.filter(id=ruler_id)
        print(spider)
        data = json.loads(request.body.decode('utf-8'))
        tem = data['tem']
        spider.update(spider_template=tem)
        spiders = ProjectRuler.objects.get(id=ruler_id)
        func = spiders.get_spider_template_display()
        spider.update(func=func)
        spi = ProjectRuler.objects.get(id=ruler_id)
        spi = spi.func
        print(spiders.get_spider_template_display())
        return JsonResponse(json.loads(json.dumps(spi)))


def add_project_scheduler(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        ids = data['ids']
        scheduler_id = data['scheduler_id']
        for id in ids:
            spider = ProjectRuler.objects.filter(id=id,is_lock=1)
            spider.update(scheduler_id=scheduler_id)
        return JsonResponse({'result': 1})


def delete_project_scheduler(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        ids = data['ids']
        scheduler_id = data['scheduler_id']
        for id in ids:
            spider = ProjectRuler.objects.filter(id=id)
            spider.update(scheduler_id=None)
        return JsonResponse({'result': 1})


"""
def spider_template(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        tem = data['tem']
        id = data['id']
        spider = ProjectRuler.objects.filter(id=id)
        print(spider)
        spider.update(spider_template=tem)
        spiders = ProjectRuler.objects.get(id=id)
        func = spiders.get_spider_template_display()
        spider.update(func=func)
        spi = ProjectRuler.objects.get(id=id)
        #spi = spi.func
        #print(spiders.get_spider_template_display())
        return JsonResponse(spi.spider_template)

"""

def user_login(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        username = data['username']
        password = data['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                # 登录成功
                login(request, user)  # 登录用户
                data = {'code': '1', 'info': u'登录成功', 'url': 'index'}
            else:
                data = {'code': '-5', 'info': u'用户未激活'}
        else:
            data = {'code': '-4', 'info': u'用户名或密码错误'}
    else:
        data = {'code': '-6', 'info': u'验证码错误'}
    return JsonResponse(data)


def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')


def choice_tem(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        tem = data['tem']
        if tem ==0:
            data = json.loads(request.body.decode('utf-8'))
            data = data.func
        else:
            p = ProjectRuler(spider_template=tem)
            #p.save()
            #print(p.get_spider_template_display())
            data = p.get_spider_template_display()
        return HttpResponse(data)

"""

def get_project_version(request,node_id,project):
    if request.method == 'GET':
        node = Node.objects.get(id=node_id)
        scrapyd = ScrapydAPI(scrapyd_url(node.node_ip,node.node_port))
        try:
            versions = scrapyd.list_versions(project)
            versions = [{'name': version, 'id': index + 1} for index, version in enumerate(versions)]
            return JsonResponse(versions)
        except ConnectionError:
            return JsonResponse({'message': 'Connect Error'}, status=500)


def remove_all_version(request,node_id,project):
    if request.method == "GET":
        node = Node.objects.get(id=node_id)
        scrapyd = ScrapydAPI(scrapyd_url(node.node_ip,node.node_port))
        try:
            versions = scrapyd.delete_project(project)
            return JsonResponse(versions)
        except ConnectionError:
            return JsonResponse({'message':'Connet Error'},status=500)

"""

def search(request):
    if request.method == "POST":
        # # all_search = ProjectRuler.objects.all()
        data = json.loads(request.body.decode('utf-8'))
        search_keywords = data.get('dept_id') or data.get('dept_name_key') or data.get('project_desc') or data.get('is_lock')
        if search_keywords:
            all_orgs = ProjectRuler.objects.filter(
                Q(project_desc__icontains=search_keywords) | Q(dept_name_key__icontains=search_keywords) \
                | Q(dept_id__icontains=search_keywords))
            try:
                while True:
                    return JsonResponse(all_orgs)
            except:
                return JsonResponse({'message':'Project does not exist'})
        else:
            return JsonResponse({'message':'Error'})


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


#错误url同步
def synfailurl(request):
    if request.method == "GET":
        failUrlList = Fail_url_detail.objects.filter(status_code="404")
        pass


def updateUrl(request):
    if request.method == "POST":
        pass