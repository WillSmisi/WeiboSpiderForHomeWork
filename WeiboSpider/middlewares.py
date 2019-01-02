# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html


import random
from WeiboSpider.cookies import Account_Cookies
from WeiboSpider.user_agents import agents

class UserAgentMiddleware(object):
    def process_request(self, request, spider):
        agent = random.choice(agents)
        request.headers["User-Agent"] = agent
class CookiesMiddleware(object):
    def process_request(self, request, spider):
        #request.cookies = random.choice(Account_Cookies)
        pass