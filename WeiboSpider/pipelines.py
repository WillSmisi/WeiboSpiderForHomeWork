# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
from scrapy.conf import settings
from WeiboSpider.items import UsrInfo,WeiboItem,WeiboItem,UserRelationItem

'''
class WeibospiderPipeline(object):
    def __init__(self):
        clinet = pymongo.MongoClient("localhost", 27017)
        db = clinet["Sina"]
        self.UsrInfo = db["UsrInfo"]
        self.Follows = db["Folllows"]
        self.Fans = db["Fans"]
        self.Weibo = db['Weibo']
        self.Repost = db['Repost']
        self.Comment = db['Comment']

    def process_item(self, item, spider):
        """ 判断item的类型，并作相应的处理，再入数据库 """
        if isinstance(item, UsrInfo):
            try:
                self.UsrInfo.insert(dict(item))
            except Exception:
                pass
        elif isinstance(item, FollowsItem):
            try:
                self.Follows.insert(dict(item))
            except Exception:
                pass
        elif isinstance(item, FansItem):
            try:
                self.Fans.insert(dict(item))
            except Exception:
                pass
        elif isinstance(item, WeiboItem):
            try:
                self.Weibo.insert(dict(item))
            except:
                pass
        elif isinstance(item, Repost):
            try:
                self.Repost.insert(dict(item))
            except:
                pass
        elif isinstance(item, Comment):
            try:
                self.Comment.insert(dict(item))
            except:
                pass
        return item

        #self.client = pymongo.MongoClient(host = settings['MONGO_HOST'], port = settings['MONGO_PORT'])
        ## 数据库登录需要帐号密码的话
        ##self.client.admin.authenticate(settings['MINGO_USER'], settings['MONGO_PSW'])
        #self.db = self.client[settings['MONGO_DB']]  # 获得数据库的句柄
        #self.coll = self.db[settings['MONGO_COLL']]  # 获得collection的句柄

    #def process_item(self, item, spider):
    #    postItem = dict(item)  # 把item转化成字典形式
    #    self.coll.insert(postItem)  # 向数据库插入一条记录
    #    #self.db['UsrInfo'].update({'uid':item['uid']}, dict(item), True)
'''


class WeiboPipeline():
    def process_item(self, item, spider):
        if isinstance(item, WeiboItem):
            if item.get('created_at'):
                item['created_at'] = item['created_at'].strip()
                item['created_at'] = self.parse_time(item.get('created_at'))


class WeibospiderPipeline(object):
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'), mongo_db=crawler.settings.get('MONGO_DB')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient("localhost", 27017)
        self.db = self.client["Sina"]
        self.db[UsrInfo.collection].create_index([('_id', pymongo.ASCENDING)])
        self.db[WeiboItem.collection].create_index([('_id', pymongo.ASCENDING)])

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item, UsrInfo) or isinstance(item, WeiboItem):
            self.db[item.collection].update({'_id': item.get('_id')}, {'$set': item}, True)
        if isinstance(item, UserRelationItem):
            self.db[item.collection].update(
                {'_id': item.get('_id')},
                {'$addToSet':
                    {
                        'follows': {'$each': item['follows']},
                        'fans': {'$each': item['fans']}
                    }
                }, True)
        return item

