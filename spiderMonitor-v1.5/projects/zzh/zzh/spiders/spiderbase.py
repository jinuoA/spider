# coding=utf-8

from scrapy import log, Request
from ..scrapy_redis.spiders import RedisCrawlSpider
import traceback
from selenium import webdriver
import time
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import json
import copy
import importlib
import hashlib
# from scrapy_splash import SplashRequest
import re
from ..date_format import get_publish_date
import MySQLdb
import datetime
import socket

from ..settings import (
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASSWD,
    MYSQL_DB,
    ZZH_LAST_MONITOR_SUBMISSION_URL
)

'''
本爬虫工程将解析部分代码由外面传入

'''

class BasesCrawler(RedisCrawlSpider):
    """Spider that reads urls from redis queue ()."""
    name = 'zzhbase'
    redis_key = 'basescrawler:rules'

    def __init__(self, *args, **kwargs):
        # Dynamically define the allowed domains list.
        domain = kwargs.pop('domain', '')
        self.allowed_domains = filter(None, domain.split(','))
        super(BasesCrawler, self).__init__(*args, **kwargs)
        self.connect = MySQLdb.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, passwd=MYSQL_PASSWD,
                                       db=MYSQL_DB,
                                       charset='utf8')
        self.cursor = self.connect.cursor()
        self.update_queue_url()
        self.update_spider_url()
        self.update_redis_time()
        self.update_spider_time()
        self.ip = self.get_host_ip()
        self.commit_item_flag_list = [0]

    meta = {
        'dont_redirect': True,  # 禁止网页重定向
        'handle_httpstatus_list': [301, 302]  # 对哪些异常返回进行处理
    }

    def parse(self, response):
        #断开mysql将解析
        self.re_connect_mysql()
        self.commit_item_flag_list[0] = 1
        self.url = response.meta['url']
        agent_ip_port = response.meta.get('agent_ip_port', self.ip)
        last_commit = False
        if response.meta['url'] == ZZH_LAST_MONITOR_SUBMISSION_URL:
            yield {'item_title': None, 'agent_ip_port': agent_ip_port, 'commit': 1}
            self.commit_item_flag_list[0] = 0
            last_commit = True
        else:
            # 失败的url存入数据库
            self.save_fail_url_detail(response)

        #种子url存入数据库
        self.save_queue_url_monitor(response, agent_ip_port, last_commit)
        #爬虫url存入数据库
        self.save_spider_url_monitor(response, agent_ip_port, last_commit)
        try:
            dept_id = response.meta['dept_id']
            dept_name_key = response.meta['dept_name_key']
            next_filter = response.meta.get('next_filter', '0')
            func = response.meta['func']
            func = func.encode('utf8')
            try:
                exec (func)
                # 该处的方法提示没有定义无影响, 和外来传入方法名一致即可
                item_list, next_page_url = parse_spider(response, dept_id, dept_name_key)
                for item in item_list:
                    item['agent_ip_port'] = agent_ip_port
                    yield item

                if next_page_url:
                    for next_page in next_page_url:
                        next_page = response.urljoin(next_page)
                        next_filter = bool(int(next_filter))
                        yield Request(next_page, self.parse, meta=response.meta,
                                      dont_filter=next_filter)
            except:
                print(traceback.format_exc())
        except:
            if last_commit:
                pass
            else:
                print(traceback.format_exc())

    def update_redis_time(self):
        # 更新时间
        self.now_base = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        # 取舍后2018-04-10 12:00:00
        self.cur_start_time = (datetime.datetime.strptime(self.now_base, "%Y-%m-%d %H:%M")).strftime(
            '%Y-%m-%d %H:%M:%S')
        self.cur_end_time = (datetime.datetime.strptime(self.now_base, "%Y-%m-%d %H:%M") + datetime.timedelta(minutes=1) - \
                             datetime.timedelta(seconds=1)).strftime('%Y-%m-%d %H:%M:%S')


    def update_spider_time(self):
        # 更新时间
        self.now_base = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        # 取舍后2018-04-10 12:00:00
        self.cur_spider_start_time = (datetime.datetime.strptime(self.now_base, "%Y-%m-%d %H:%M")).strftime(
            '%Y-%m-%d %H:%M:%S')
        self.cur_spider_end_time = (datetime.datetime.strptime(self.now_base, "%Y-%m-%d %H:%M") + datetime.timedelta(minutes=1) - \
                             datetime.timedelta(seconds=1)).strftime('%Y-%m-%d %H:%M:%S')

    def update_queue_url(self):
        self.total_queue_url = 0
        self.success_queue_url = 0
        # self.fail_queue_url = 0
        # self.status_403_queue_url = 0
        # self.status_404_queue_url = 0
        # self.status_other_queue_url = 0
        self.queue_url_list = []
        self.queue_url_dict_list = []

    def update_spider_url(self):
        self.total_url = 0
        self.success_url = 0
        # self.fail_url = 0
        # self.status_403_url = 0
        # self.status_404_url = 0
        # self.status_50x_url = 0
        # self.status_other_url =0

    def re_connect_mysql(self):
        try:
            self.connect.ping()
        except:
            self.connect = MySQLdb.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, passwd=MYSQL_PASSWD,
                                           db=MYSQL_DB,charset='utf8')
            self.cursor = self.connect.cursor()

    def save_fail_url_detail(self, response):
        if response.status != 200:
            # 断开mysql将不统计数据
            #self.re_connect_mysql()
            queue_url = response.meta['url']
            spider_url = response.url
            status_code = response.status
            save_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            dept_id = response.meta['dept_id']
            dept_name_key = response.meta['dept_name_key']
            sql = """insert into zzh_fail_url_detail \
                      (queue_url,spider_url,status_code, save_time,dept_id, dept_name_key)\
                      values(%s,%s,%s,%s,%s, %s);"""
            argsList = (queue_url, spider_url, status_code, save_time, dept_id, dept_name_key)
            self.cursor.execute(sql, argsList)
            self.connect.commit()

    def save_queue_url_monitor(self, response, agent_ip_port, last_commit):
        # 场景一: 种子url夸时间, 如第一次爬有500页的种子url从4:40到5:20,
        # 处理： 4到5点算一次，5到6点算一次
        # 断开mysql将不统计数据
        #self.re_connect_mysql()

        #场景一，一个种子url在一分钟爬取3个子url,一个成功，2个状态码不一样的失败，统统的失败的 :1, 0, 1
        #前面的已经把失败的url存入数据了, 非200的状态码改成600, 一个种子url有失败的url，该时刻成功从种子url为0
        if not last_commit:
            if response.url == response.meta['url']:
                self.total_queue_url += 1
                if response.status == 200:
                    self.success_queue_url += 1

        cur_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if cur_time > self.cur_end_time or last_commit:
            if last_commit:
                self.update_redis_time()
            insertStr = """insert into zzh_queue_url_monitor \
                                   (total_queue_url, success_queue_url, start_time, end_time, agent_ip_port) \
                                    values(%s, %s, %s, %s, %s);"""
            start_time = datetime.datetime.strptime(self.cur_start_time, "%Y-%m-%d %H:%M:%S")
            end_time = datetime.datetime.strptime(self.cur_end_time, "%Y-%m-%d %H:%M:%S")
            argsList = (self.total_queue_url, self.success_queue_url, start_time, \
                        end_time, agent_ip_port)
            try:
                self.cursor.execute(insertStr, argsList)
                self.connect.commit()
            except:
                print(traceback.format_exc())
            self.update_queue_url()
            if not last_commit:
                self.update_redis_time()

    def save_spider_url_monitor(self, response, agent_ip_port, last_commit):
        # 断开mysql将不统计数据
        #self.re_connect_mysql()
        if not last_commit:
            self.total_url += 1
            if response.status == 200:
                self.success_url += 1
        cur_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if cur_time > self.cur_spider_end_time or last_commit:
            if last_commit:
                self.update_spider_time()

            insertStr = """insert into zzh_spider_url_monitor \
                           (total_url, success_url, start_time, end_time, agent_ip_port) \
                            values(%s, %s, %s, %s, %s);"""

            start_time = datetime.datetime.strptime(self.cur_spider_start_time, "%Y-%m-%d %H:%M:%S")
            end_time = datetime.datetime.strptime(self.cur_spider_end_time, "%Y-%m-%d %H:%M:%S")
            argsList = (self.total_url, self.success_url, start_time,end_time, agent_ip_port)
            try:
                self.cursor.execute(insertStr, argsList)
                self.connect.commit()
            except:
                print(traceback.format_exc())

            self.update_spider_url()
            if not last_commit:
                self.update_spider_time()

    def get_host_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()

        return ip