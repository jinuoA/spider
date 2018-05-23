# encoding=utf-8
import random
import scrapy
from scrapy import log
import time
import os
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware


from .conf.user_agents import (
    agents
)

# logger = logging.getLogger()
class ProxyMiddleWare(object):
    """docstring for ProxyMiddleWare"""

    def process_request(self, request, spider):
        '''对request对象加上proxy'''
        proxy = self.get_random_proxy()
        if request.meta.get('splash', None):
            print("this is splash request ip:" + proxy)
            request.meta['splash']['args']['proxy'] = proxy
            request.headers["Proxy-Authorization"] = proxy
        else:
            print("this is request ip:" + proxy)
            request.meta['proxy'] = proxy

    def process_response(self, request, response, spider):
        '''对返回的response处理'''
        # 如果返回的response状态不是200，重新生成当前request对象
        if response.status != 200:
            proxy = self.get_random_proxy()
            print("this is response ip:" + proxy)
            if request.meta.get('splash', None):
                print("this is splash request ip:" + proxy)
                request.meta['splash']['args']['proxy'] = proxy
                request.headers["Proxy-Authorization"] = proxy
            else:
                print("this is request ip:" + proxy)
                request.meta['proxy'] = proxy

            return request
        return response

    def get_random_proxy(self):
        '''随机从文件中读取proxy'''
        path = os.path.dirname(os.path.realpath(__file__))
        while 1:
            with open(path +'\\conf\\ip_proxy.ini', 'r') as f:
                proxies = f.readlines()
            if proxies:
                break
            else:
                time.sleep(1)
        proxy = random.choice(proxies).strip()
        return proxy

#url_agent
class RotateUserAgentMiddleware(object):
    """docstring for url_agent"""

    def __init__(self, user_agent=''):
        self.user_agent = user_agent
        self.reconnect_num = 0

    def process_request(self, request, spider):
        url_agent = random.choice(agents)
        if url_agent:
            print('this is User-Agent', url_agent)
            request.headers.setdefault('User-Agent', url_agent)

    def process_response(self, request, response, spider):
        '''对返回的response处理, setting禁止重定向的'''
        # 如果返回的response状态不是200，重新生成当前request对象
        #200请求成功、301重定向, 302临时重定向,
        # 303重定向、400请求错误、401未授权、403禁止访问、404文件未找到、500服务器错误
        status_code = [200, 301, 302, 303, 404, 500]
        if response.status not in status_code:
            self.reconnect_num += 1
            if self.reconnect_num > 9:
                self.reconnect_num = 0
                return response
            url_agent = random.choice(agents)
            print("response.status:", response.status)
            print("restart agent:" + url_agent)
            # 对当前reque加上代理
            request.headers.setdefault('User-Agent', url_agent)
            return request
        return response





