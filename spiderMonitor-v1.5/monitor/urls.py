from django.conf.urls import url
from django.urls import include, path, re_path
from . import views

urlpatterns = [
    url(r'^api/monitor/itemMonitorDay/$', views.itemMonitorDay, name='itemMonitorDay'), #test1  itemMonitorDay
    url(r'^api/monitor/queueMonitorDay/$', views.queueMonitorDay, name='queueMonitorDay'), #test1  queueMonitorDay
    url(r'^api/monitor/spiderMonitorDay/$', views.spiderMonitorDay, name='spiderMonitorDay'), #test1  queueMonitorDay
    url(r'^api/monitor/itemMonitorMonth/$', views.itemMonitorMonth, name='itemMonitorMonth'), #test1  itemMonitorMonth
    url(r'^api/monitor/itemMonitorWeek/$', views.itemMonitorWeek, name='itemMonitorWeek'), #test1  itemMonitorWeek
    url(r'^api/monitor/monitorMonth/$', views.monitorMonth, name='monitorMonth'), #test2
    url(r'^api/monitor/monitorWeek/$', views.monitorWeek, name='monitorWeek'), #test3
    url(r'^api/addtemplate/$', views.addTemplate, name='addTemplate'), #test4
    url(r'^api/failUrlList/$', views.failUrlList, name='failUrlList'), #test5
    url(r'^api/FailUrlSearch/$', views.FailUrlSearch, name='FailUrlSearch'), #test5
    url(r'^api/failUrlDetail/$', views.failUrlDetail, name='failUrlDetail'), #test5
    url(r'^api/taskUrlSearch/$', views.taskUrlSearch, name='taskUrlSearch'), #zhuaqujieguo
    url(r'^api/failUrlLists/$', views.failUrlLists, name='failUrlLists'), #zhuaqujieguo  failUrlSearch
    path(r'fail/url/', views.fail_url, name='fail_url'),
    path(r'item/data', views.avalidItem,name='itemdata'),
    path(r'download/', views.excel_export), #有效增加数据
    path(r'download/fail/url/', views.excel_export_url), #有效增加数据
    # path(r'item/data/ss', views.export_data), #有效增加数据
    path(r'item_monitor/', views.item_monitor,name="item_monitor"), #item_monitor
    path(r'queue_monitor/', views.queue_monitor,name="queue_monitor"), #queue_monitor
    path(r'spider_monitor/', views.spider_monitor,name="spider_monitor"), #spider_monitor
    path(r'item_monitor_month/', views.item_monitor_month,name="item_monitor_month"), #item_monitor_month
    path(r'item_monitor_week/', views.item_monitor_week,name="item_monitor_week"), #item_monitor_month




]
