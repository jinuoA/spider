# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.utils.serialize import ScrapyJSONEncoder

from kafka.client import SimpleClient
from kafka.producer import SimpleProducer
from .zzhtitlematch import TitleMatchMethod
import traceback
import os
import MySQLdb
import time
import datetime
import sched
import traceback

from .settings import (
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASSWD,
    MYSQL_DB
)

#多个机器上执行爬虫 数据统计输入ip+port, 默认是本机ip
#爬虫在时间段中间, 或断断续续的推送到队列, 后面的无法统计问题,以分钟为单位,添加最后一次提交标志
#提交完成后不需要关闭mysql连接, 在类的构造函数中整个爬虫只调用一次,
#下次只需要ping是否连接即可，不会出现每次连接数据增加的问题
class KafkaPipeline(object):
    """
    Publishes a serialized item into a Kafka topic
    :param producer: The Kafka producer
    :type producer: kafka.producer.Producer
    :param topic: The Kafka topic being used
    :type topic: str or unicode
    """

    def __init__(self, producer, topic, invail_item_topic):
        """
        :type producer: kafka.producer.Producer
        :type topic: str or unicode
        """
        self.producer = producer
        self.topic = topic
        self.invail_item_topic = invail_item_topic
        self.encoder = ScrapyJSONEncoder()
        self.tmp_list = []
        self.connect = MySQLdb.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, passwd=MYSQL_PASSWD,
                                  db=MYSQL_DB,
                                  charset='utf8')
        self.cursor = self.connect.cursor()
        self.update_time()

    def process_item(self, item, spider):
        """
        Overriden method to process the item
        :param item: Item being passed
        :type item: scrapy.item.Item
        :param spider: The current spider being used
        :type spider: scrapy.spider.Spider
        """
        #断开mysql将不统计数据
        self.re_connect_mysql()
        item = dict(item)
        item['time_str'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item_title = item['item_title']
        if item_title:
            self.item_total += 1
            msg = self.encoder.encode(item)
            item_title_bool = TitleMatchMethod(str(item_title.encode('utf-8')))
            if item_title_bool:
                self.producer.send_messages(self.topic, msg)
                self.avail_item += 1
                # 当前时间数据正在存入, 需要统计当前的数据  2018-04-10 12:00:00 - 2018-04-10 12:59:59
                cur_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                #当前时间和上一时刻的取入时间判断
                if cur_time > self.cur_end_time:
                    self.save_item_monitor(item)
                    self.update_time()
            else:
                self.producer.send_messages(self.invail_item_topic, msg)
                self.invalid_item += 1
                # 当前时间数据正在存入, 需要统计当前的数据  2018-04-10 12:00:00 - 2018-04-10 12:59:59
                cur_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                if cur_time > self.cur_end_time:
                    self.save_item_monitor(item)
                    self.update_time()

        else:
            if item.get('commit', 0) == 1:
                # 更新时间
                self.now_base = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                # 取舍后2018-04-10 12:00:00
                self.cur_start_time = (datetime.datetime.strptime(self.now_base, "%Y-%m-%d %H:%M")).strftime(
                    '%Y-%m-%d %H:%M:%S')
                self.cur_end_time = ( datetime.datetime.strptime(self.now_base, "%Y-%m-%d %H:%M") + datetime.timedelta(minutes=1) - \
                datetime.timedelta(seconds=1)).strftime('%Y-%m-%d %H:%M:%S')

                self.save_item_monitor(item)
                self.update_time()


    @classmethod
    def from_settings(cls, settings):
        """
        :param settings: the current Scrapy settings
        :type settings: scrapy.settings.Settings
        :rtype: A :class:`~KafkaPipeline` instance
        """
        k_hosts = settings.get('SCRAPY_KAFKA_HOSTS', '127.0.0.1:9092')
        topic = settings.get('SCRAPY_KAFKA_ITEM_PIPELINE_TOPIC', 'data-topic')
        invail_item_topic = settings.get('SCRAPY_KAFKA_INVAILID_ITEM_PIPELINE_TOPIC', 'invalid_item')
        client = SimpleClient(k_hosts)
        producer = SimpleProducer(client)
        return cls(producer, topic, invail_item_topic)

    def update_time(self):
        # 更新时间
        self.now_base = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        # 取舍后2018-04-10 12:00:00
        self.cur_start_time = (datetime.datetime.strptime(self.now_base, "%Y-%m-%d %H:%M")).strftime(
            '%Y-%m-%d %H:%M:%S')
        self.cur_end_time = (datetime.datetime.strptime(self.now_base, "%Y-%m-%d %H:%M") + datetime.timedelta(minutes=1) - \
            datetime.timedelta(seconds=1)).strftime('%Y-%m-%d %H:%M:%S')

        #归0
        self.item_total = 0
        self.avail_item = 0
        self.invalid_item = 0
        #self.item_avail_increased = 0

        #全部变量标志, 监控断断续续的提交


    def re_connect_mysql(self):
        try:
            self.connect.ping()
        except:
            self.connect = MySQLdb.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, passwd=MYSQL_PASSWD,
                                           db=MYSQL_DB,
                                           charset='utf8')
            self.cursor = self.connect.cursor()


    def save_item_monitor(self, item):
        insertStr = """insert into zzh_item_monitor \
                       (item_total, item_avail, item_invalid, start_time, end_time, agent_ip_port) \
                       values(%s, %s, %s, %s, %s, %s);"""
        start_time = datetime.datetime.strptime(self.cur_start_time, "%Y-%m-%d %H:%M:%S")
        end_time = datetime.datetime.strptime(self.cur_end_time, "%Y-%m-%d %H:%M:%S")
        agent_ip_port = item['agent_ip_port']
        argsList = (
        self.item_total, self.avail_item, self.invalid_item, start_time, end_time,agent_ip_port)
        try:
            self.cursor.execute(insertStr, argsList)
            self.connect.commit()
        except:
            print(traceback.format_exc())