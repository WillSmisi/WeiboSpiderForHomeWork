#coding=utf-8

import scrapy
import re
import time
import json
from scrapy.http import Request
from WeiboSpider.items import UsrInfo,UserRelationItem,WeiboItem
#from WeiboSpider.items import FansItem, UsrInfo, FollowsItem, WeiboItem, Repost, Comment
import requests
import csv

class WeiboSpider(scrapy.Spider):
    name = 'WeiboSpider'
    user_id = []
    with open('D:/Harmonycloud/school/fan.txt', 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line[:-1]
            user_id.append(line)
    print(len(user_id))
    print(user_id)
    scrawl_ID = set(user_id)
    finish_ID = set()
    user_url = 'https://m.weibo.cn/api/container/getIndex?uid={uid}&type=uid&value={uid}&containerid=100505{uid}'
    follow_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_{uid}&page={page}'
    fan_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_{uid}&page={page}'
    weibo_url = 'https://m.weibo.cn/api/container/getIndex?uid={uid}&type=uid&page={page}&containerid=107603{uid}'


    def start_requests(self):
        while self.scrawl_ID.__len__():
            ID = self.scrawl_ID.pop()
            self.finish_ID.add(ID)
            yield Request(self.user_url.format(uid=ID),meta={'start':1},callback=self.parse_user)
            '''
            url_info = 'https://m.weibo.cn/api/container/getIndex?containerid=230283' + ID + '_-_INFO&title=%25E5%259F%25BA%25E6%259C%25AC%25E4%25BF%25A1%25E6%2581%25AF&luicode=10000011&lfid=230283' + ID
            new_url_info = 'https://m.weibo.cn/api/container/getIndex?uid=' + ID + '&type=uid&value=' + ID + '&containerid=100505' + ID
            url_fan = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_' + ID + '&featurecode=20000320&since_id=1'
            url_follow = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_' + ID + '&featurecode=20000320&page=1'
            '''
            '''
            fans = []
            fansItems = FansItem()
            fansItems["_id"] = ID
            fansItems["fans_list"] = fans

            follows = []
            followsItems = FollowsItem()
            followsItems["_id"] = ID
            followsItems["follows_list"] = follows
            '''
            #yield Request(url_fan, meta={"item": fansItems, "result": fans}, callback=self.getFans)
            #yield Request(url_follow, meta={"item": followsItems, "result": follows}, callback=self.getFollow)
            #yield Request(url_info, meta={"ID": ID}, callback=self.getUsrInfo)
            #print(self.fan)

    def parse_user(self, response):
        result = json.loads(response.text)
        if result.get('data').get('userInfo'):
            user_info = result.get('data').get('userInfo')
            user_item = UsrInfo()
            field_map = {
                '_id': 'id', 'name': 'screen_name', 'avatar': 'profile_image_url', 'cover': 'cover_image_phone',
                'gender': 'gender', 'description': 'description', 'fans_count': 'followers_count',
                'follows_count': 'follow_count', 'weibos_count': 'statuses_count', 'verified': 'verified',
                'verified_reason': 'verified_reason', 'verified_type': 'verified_type'
            }
            for field, attr in field_map.items():
                if field =='_id':
                    user_item[field] = str(user_info.get(attr))
                else:
                    user_item[field] = user_info.get(attr)
            yield user_item
            # 关注
            uid = user_info.get('id')
            start = int(response.meta['start'])

            yield Request(self.follow_url.format(uid=uid, page=1), callback=self.parse_follows,
                          meta={'page': 1, 'uid': uid,'start':1})
            # 粉丝
            yield Request(self.fan_url.format(uid=uid, page=1), callback=self.parse_fans,
                          meta={'page': 1, 'uid': uid,'start':1})
            # 微博
            yield Request(self.weibo_url.format(uid=uid, page=1), callback=self.parse_weibos,
                          meta={'page': 1, "count": 1,'uid': uid,'start':1})

    def parse_follows(self, response):
        """
        解析用户关注
        :param response: Response对象
        """
        start = int(response.meta['start'])
        result = json.loads(response.text)
        print(start)
        if result['ok'] == 0:
            return
        if result.get('ok') and result.get('data').get('cards') and len(result.get('data').get('cards')) and \
                result.get('data').get('cards')[-1].get(
                        'card_group'):
            # 解析用户
            follows = result.get('data').get('cards')[-1].get('card_group')
            '''
            for follow in follows:
                if follow.get('user'):
                    uid = follow.get('user').get('id')
                    yield Request(self.user_url.format(uid=uid),meta={'start':start+1}, callback=self.parse_user)
            '''
            # 关注列表
            uid = response.meta.get('uid')
            user_relation_item = UserRelationItem()
            follows = [{'_id': str(follow.get('user').get('id')), 'name': follow.get('user').get('screen_name')} for follow in
                       follows]
            user_relation_item['_id'] = str(uid)
            user_relation_item['follows'] = follows
            user_relation_item['fans'] = []
            flag = result['ok']
            if flag == 0:
                yield user_relation_item
            # yield user_relation_item
            # 下一页关注
            else:
            #yield user_relation_item
            # 下一页关注
                page = response.meta.get('page') + 1
                if page ==8:
                    yield user_relation_item
                if (page > 8):
                    return
                yield Request(self.follow_url.format(uid=uid, page=page),
                          callback=self.parse_follows, meta={'page': page, 'uid': uid,'start':start})

    def parse_fans(self, response):
        """
        解析用户关注
        :param response: Response对象
        """
        start = int(response.meta['start'])
        result = json.loads(response.text)
        if result['ok'] == 0:
            return
        if result.get('ok') and result.get('data').get('cards') and len(result.get('data').get('cards')) and \
                result.get('data').get('cards')[-1].get(
                        'card_group'):
            # 解析用户
            fans = result.get('data').get('cards')[-1].get('card_group')
            '''
            for fan in fans:
                if fan.get('user'):
                    uid = fan.get('user').get('id')
                    yield Request(self.user_url.format(uid=uid),meta={'start':start+1}, callback=self.parse_user)
            '''
            # 关注列表
            uid = response.meta.get('uid')
            user_relation_item = UserRelationItem()
            fans = [{'_id': str(fan.get('user').get('id')), 'name': fan.get('user').get('screen_name')} for fan in
                       fans]
            user_relation_item['_id'] = str(uid)
            user_relation_item['follows'] = []
            user_relation_item['fans'] = fans
            flag = result['ok']
            if flag == 0:
                yield user_relation_item
            #yield user_relation_item
            # 下一页关注
            else:
                page = response.meta.get('page') + 1
                if page ==8:
                    yield user_relation_item
                if (page > 8):
                    return
                yield Request(self.fan_url.format(uid=uid, page=page),
                          callback=self.parse_fans, meta={'page': page, 'uid': uid,'start':start})

    def parse_weibos(self, response):
        """
        解析微博列表
        :param response: Response对象
        """
        count = int(response.meta['count'])
        result = json.loads(response.text)
        if result['ok'] == 0:
            return

        if result.get('ok') and result.get('data').get('cards'):
            weibos = result.get('data').get('cards')
            for weibo in weibos:
                mblog = weibo.get('mblog')
                if count == 101:
                    return
                if mblog:
                    weibo_item = WeiboItem()
                    field_map = {
                        '_id': 'id', 'attitudes_count': 'attitudes_count', 'comments_count': 'comments_count',
                        'created_at': 'created_at',
                        'reposts_count': 'reposts_count', 'picture': 'original_pic', 'pictures': 'pics',
                        'source': 'source', 'text': 'text', 'raw_text': 'raw_text', 'thumbnail': 'thumbnail_pic'
                    }
                    for field, attr in field_map.items():
                        weibo_item[field] = mblog.get(attr)
                    weibo_item['user'] = str(response.meta.get('uid'))
                    count =count+1
                    yield weibo_item
            # 下一页微博
            uid = response.meta.get('uid')
            page = response.meta.get('page') + 1
            if (page > 30):
                return
            yield Request(self.weibo_url.format(uid=uid, page=page), callback=self.parse_weibos,
                          meta={'uid': uid, 'page': page,'count' : int(response.meta['count'])})

    def parse_time(self, date):
        if re.match('刚刚', date):
            date = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
        if re.match('\d+分钟前', date):
            minute = re.match('(\d+)', date).group(1)
            date = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time() - float(minute) * 60))
        if re.match('\d+小时前', date):
            hour = re.match('(\d+)', date).group(1)
            date = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time() - float(hour) * 60 * 60))
        if re.match('昨天.*', date):
            date = re.match('昨天(.*)', date).group(1).strip()
            date = time.strftime('%Y-%m-%d', time.localtime() - 24 * 60 * 60) + ' ' + date
        if re.match('\d{2}-\d{2}', date):
            date = time.strftime('%Y-', time.localtime()) + date + ' 00:00'
        return date

    def getFollow(self, response):
        follows = response.meta['item']
        ob_json = json.loads(response.text)
        flag = ob_json['ok']
        if flag == 0:
            return

        uid = str(ob_json['data']['cardlistInfo']['containerid'][-10:])
        next_page = str(ob_json['data']['cardlistInfo']['page'])
        list_cards = ob_json['data']['cards']
        card = list_cards[len(list_cards) - 1]['card_group']
        for i in range(len(card)):
            id = str(card[i]['user']['id'])
            if len(str(id)) > 10:
                continue
            response.meta['result'].append(id)

        next_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_'+ uid +'&featurecode=20000320&page=' + next_page
        next = requests.get(next_url)
        objson = json.loads(next.text)
        flag = objson['ok']
        if flag == 0:
            yield follows
        else:
            yield Request(next_url, meta = {"item": follows, "result": response.meta["result"]}, callback = self.getFollow)

    def getFans(self, response):
        fans = response.meta['item']
        ob_json = json.loads(response.text)

        if ob_json['ok'] == 0:
            return

        uid = str(ob_json['data']['cardlistInfo']['containerid'][-10:])

        next_page = str(ob_json['data']['cardlistInfo']['since_id'])
        list_cards = ob_json['data']['cards'][0]['card_group']
        for card in list_cards:
            id = str(card['user']['id'])
            response.meta['result'].append(id)

        next_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_'+ uid +'&featurecode=20000320&since_id=' + next_page

        next = requests.get(next_url)
        objson = json.loads(next.text)
        flag = objson['ok']
        if flag == 0:
            yield fans
        else:
            yield Request(next_url, meta={"item": fans, "result": response.meta["result"]}, callback = self.getFans)


    def getUsrInfo(self, response):
        ob_json = json.loads(response.text)
        if ob_json.get('data').get('userInfo'):
            user_info = ob_json.get('data').get('userInfo')
            #user_item = UserItem()
            usrInfo = UsrInfo()

        #card = ob_json['data']['cards'][0]['card_group']
        field_map = {
            'id': 'id', 'name': 'screen_name', 'avatar': 'profile_image_url', 'cover': 'cover_image_phone',
            'gender': 'gender', 'description': 'description', 'fans_count': 'followers_count',
            'follows_count': 'follow_count', 'weibos_count': 'statuses_count', 'verified': 'verified',
            'verified_reason': 'verified_reason', 'verified_type': 'verified_type'
        }
        for field, attr in field_map.items():
            usrInfo[field] = user_info.get(attr)
        uid = response.meta['ID']
        '''
        uid = response.meta['ID']
        usrInfo['_id'] = uid
        usrInfo['nickname'] = ''
        usrInfo['tag'] = ''
        usrInfo['sex'] = ''
        usrInfo['province'] = ''
        usrInfo['city'] = ''
        usrInfo['desc'] = ''
        '''
        '''
        for i in range(len(card)):
            if 'item_name' not in card[i].keys():
                continue
            if card[i]['item_name'] == '昵称':
                usrInfo['nickname'] = card[i]['item_content']
            elif card[i]['item_name'] == '标签':
                usrInfo['tag'] = card[i]['item_content']
            elif card[i]['item_name'] == '性别':
                usrInfo['sex'] = card[i]['item_content']
            elif card[i]['item_name'] == '所在地':
                add = card[i]['item_content'].split(' ')
                usrInfo['province'] = add[0]
                if len(add) > 1:
                    usrInfo['city'] = add[1]
            elif card[i]['item_name'] == '简介':
                usrInfo['desc'] = card[i]['item_content']
            '''

        yield usrInfo
        url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value='+uid+'&containerid=107603'+uid+'&page=1'
        yield Request(url, meta={"ID": uid, "count": 1,'page': 1}, callback=self.getWeibo)

    def getWeibo(self, response):
        count = int(response.meta['count'])
        print(count)
        ob_json = json.loads(response.text)
        if ob_json['ok'] == 0:
            return
        list_cards = ob_json['data']['cards']
        next_page = str(ob_json['data']['cardlistInfo']['page'])
        #print(next_page)
        for card in list_cards:
            if count == 101:
                return
            weibo = WeiboItem()
            weibo['uid'] = response.meta['ID']
            if card['card_type'] != 9:
                continue
            weibo['time'] = card['mblog']['created_at']
            weibo['attitudes_count'] = card['mblog']['attitudes_count']
            weibo['comments_count'] = card['mblog']['comments_count']
            weibo['reposts_count'] = card['mblog']['reposts_count']
            weibo['weibo_id'] = card['mblog']['id']
            weibo['_id'] = weibo['uid'] + weibo['weibo_id']
            if 'raw_text' in card['mblog']:
                weibo['content'] = card['mblog']['raw_text']
            else:
                weibo['content'] = card['mblog']['text']

            #reposts = []
            #repostItem = Repost()
            #repostItem['_id'] = weibo['weibo_id']
            #repostItem['uid'] = weibo['uid']
            #repostItem["repost_list"] = reposts
            #
            #yield Request('https://m.weibo.cn/api/statuses/repostTimeline?id=' + weibo['weibo_id'] + '&page=1',
            #             meta={"item": repostItem, "result": reposts, "page": 1},
            #             callback=self.getRepost)
            #
            #comments = []
            #commentItem = Comment()
            #commentItem['_id'] = weibo['weibo_id']
            #commentItem['uid'] = weibo['uid']
            #commentItem["comment_list"] = comments
            #yield Request('https://m.weibo.cn/api/comments/show?id=' + weibo['weibo_id'] + '&page=1',
            #              meta={"item": commentItem, "result": comments, "page": 1},
            #              callback=self.getComment)

            count += 1
            yield weibo

        next_url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=' + weibo['uid'] + '&containerid=107603' + weibo['uid'] + '&page=' + next_page
        yield Request(next_url, meta={"ID": weibo['uid'], "count": str(count)}, callback=self.getWeibo)



    def getRepost(self, response):
        repost = response.meta['item']
        w_id = repost['_id']
        ob_json = json.loads(response.text)
        if ob_json['ok'] == 0:
            return
        list_cards = ob_json['data']['data']
        for card in list_cards:
            repost['repost_list'].append(str(card['user']['id']))

        next_page = str(int(response.meta['page']) + 1)
        #print(next_page)
        next_url = 'https://m.weibo.cn/api/statuses/repostTimeline?id=' + w_id + '&page=' + next_page
        next = requests.get(next_url)
        objson = json.loads(next.text)
        flag = objson['ok']
        if flag == 0:
            yield repost
        else:
            yield Request(next_url, meta={"item": repost, "result": response.meta["result"], "page": next_page},
                          callback=self.getRepost)

    def getComment(self, response):
        comment = response.meta['item']
        w_id = comment['_id']
        ob_json = json.loads(response.text)
        if ob_json['ok'] == 0:
            return
        list_cards = ob_json['data']['data']
        for card in list_cards:
            comment['comment_list'].append(str(card['user']['id']))

        next_page = str(int(response.meta['page']) + 1)
        next_url = 'https://m.weibo.cn/api/statuses/repostTimeline?id=' + w_id + '&page=' + next_page
        next = requests.get(next_url)
        objson = json.loads(next.text)
        flag = objson['ok']
        if flag == 0:
            yield comment
        else:
            yield Request(next_url, meta={"item": comment, "result": response.meta["result"], "page": next_page},
                          callback=self.getComment)