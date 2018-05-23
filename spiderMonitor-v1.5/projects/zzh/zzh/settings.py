# -*- coding: utf-8 -*-
# Scrapy settings for example project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#
SPIDER_MODULES = ['zzh.spiders']
NEWSPIDER_MODULE = 'zzh.spiders'

DUPEFILTER_CLASS = "zzh.scrapy_redis.dupefilter.RFPDupeFilter"
SCHEDULER = "zzh.scrapy_redis.scheduler.Scheduler"
SCHEDULER_PERSIST = True
SCHEDULER_QUEUE_CLASS = "zzh.scrapy_redis.queue.SpiderPriorityQueue"


# 种子队列的信息
REDIS_HOST = '192.168.5.127'
REDIS_PORT = 6380

# 去重url队列的信息
FILTER_URL = None
FILTER_HOST = '192.168.5.127'
FILTER_PORT = 6380
FILTER_DB = 0


#reference URL http://wiki.jikexueyuan.com/project/scrapy/broad-crawls.html
LOG_LEVEL = 'INFO'
CONCURRENT_REQUESTS = 100
CONCURRENT_REQUESTS_PER_SPIDER = 5
COOKIES_ENABLED = False
RETRY_ENABLED = False
CLOSESPIDER_PAGECOUNT = 100000
#CLOSESPIDER_TIMEOUT = 36000 #默认是0，spiders不会因为超时而关闭
DOWNLOAD_DELAY = 1.5
DOWNLOAD_TIMEOUT = 15
REDIRECT_ENABLED = False
AJAXCRAWL_ENABLED = True
HTTPERROR_ALLOWED_CODES = [404, 403, 408, 500, 502, 301, 302]
#LOG_FILE = "zzhbase.log"
#kafka
SCRAPY_KAFKA_ITEM_PIPELINE_TOPIC = "data-topic"
SCRAPY_KAFKA_INVAILID_ITEM_PIPELINE_TOPIC = "invalid_item"
SCRAPY_KAFKA_HOSTS = "192.168.5.125:9092"

#mysql conf
MYSQL_HOST = '192.168.5.125'
MYSQL_PORT = 3305
MYSQL_USER = 'root'
MYSQL_PASSWD = 'root1234'
MYSQL_DB = 'url'


#priority: Low orders are closer to the engine, high orders are closer to the spider
DOWNLOADER_MIDDLEWARES = {

 # 'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware':None,
 # 'scrapyWithBloomfilter_demo.middlewares.ProxyMiddleWare':843,
 # 'scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware':None,

 'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
 'zzh.middlewares.RotateUserAgentMiddleware': 900,
}

ITEM_PIPELINES = {
    'zzh.pipelines.KafkaPipeline': 300,
}

#SPLASH_URL = 'http://192.168.5.127:8050'
#DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
#HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'
#splash
#DOWNLOADER_MIDDLEWARES = {
#    'scrapy_splash.SplashCookiesMiddleware': 723,
#    'scrapy_splash.SplashMiddleware': 725,
 #   'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
#}


#USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
#REDIS_URL = 'redis://127.0.0.1:6379'


#用于监控数据，触发非整点数据提交, 或断断续续的往队列中推url
ZZH_LAST_MONITOR_SUBMISSION_URL = 'http://127.0.0.1:6800'




