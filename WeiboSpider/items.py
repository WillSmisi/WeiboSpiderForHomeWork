# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.org/en/latest/topics/items.html


from scrapy import Item, Field

class UsrInfo(Item):
    collection = 'users'
    _id = Field()
    name = Field()
    avatar = Field()
    cover = Field()
    gender = Field()
    description = Field()
    fans_count = Field()
    follows_count = Field()
    weibos_count = Field()
    verified = Field()
    verified_reason = Field()
    verified_type = Field()
    follows = Field()
    fans = Field()
    crawled_at = Field()


class UserRelationItem(Item):
    collection = 'users'
    _id = Field()
    follows = Field()
    fans = Field()


class WeiboItem(Item):
    collection = 'weibos'
    _id = Field()
    attitudes_count = Field()
    comments_count = Field()
    reposts_count = Field()
    picture = Field()
    pictures = Field()
    source = Field()
    text = Field()
    raw_text = Field()
    thumbnail = Field()
    user = Field()
    created_at = Field()
    crawled_at = Field()
'''
class FollowsItem(Item):
    _id = Field()
    follows_list = Field() #关注列表

class FansItem(Field):
    _id = Field()
    fans_list = Field()#粉丝列表

class WeiboItem(Field):
    _id = Field() #用户ID+微博ID
    weibo_id = Field()
    uid = Field()
    time = Field()
    repost_count = Field()
    attitudes_count = Field()
    comments_count = Field()
    content = Field()
    #repost_list = Field()
    #comment_list = Field()

class Repost(Field):
    _id = Field()
    uid = Field()
    repost_list = Field()

class Comment(Field):
    _id = Field()
    uid = Field()
    comment_list = Field()

'''