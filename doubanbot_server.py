#!/usr/bin/python
# coding=utf-8

### 豆瓣小组抢楼机器人 server版本

__author__ = "maniacmike"


import sys, getopt
import urllib, urllib2
import cookielib
import requests
import json
import time
import random
from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint


class GroupHtmlParser(HTMLParser):
    def __init__(self):
        self.processing = False
        self.currentId = ""
        self.topicIds = []
        self.ck = ""
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        linkStart = "https://www.douban.com/group/topic/"
        linkLogoutStart = "https://www.douban.com/accounts/logout"
        if tag == "a" and len(attrs) > 2 and attrs[0][1][0:len(linkStart)] == linkStart:
            self.currentId = attrs[0][1][len(linkStart):]
            self.currentId = self.currentId[0:-1]
        elif tag == "a" and len(attrs) > 0 and attrs[0][1][0:len(linkLogoutStart)] == linkLogoutStart:
            self.ck = attrs[0][1][-4:]
        elif tag == "td" and len(attrs) > 1 and attrs[0][1] == "td-reply":
            self.processing = True
        else:
            self.processing = False

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        if self.processing and data[0:1] == "0":
            # print(self.currentId)
            self.topicIds.append(self.currentId)

    def get_data(self):
        return (self.ck, self.topicIds)


class UnicodeStreamFilter:
	def __init__(self, target):
		self.target = target
		self.encoding = 'utf-8'
		self.errors = 'replace'
		self.encode_to = self.target.encoding

	def write(self, s):
		if type(s) == str:
			s = s.decode('utf-8')
		s = s.encode(self.encode_to, self.errors).decode(self.encode_to)
		self.target.write(s)

	def flush(self):
		self.target.flush()

def loginDouban(email,password):
    loginUrl = "https://www.douban.com/accounts/login"
    params = {
        "source" : "index_nav",
        "form_email" : email,
        "form_password" : password
    }
    _post(loginUrl, params)

def postDoubanComment(ck,content,tid):
    commentUrl = "https://www.douban.com/group/topic/"+tid+"/add_comment"
    params = {
        "ck" : ck,
        "rv_comment" : content,
		"start" : 0,
        "submit_btn" : "加上去"
    }
    _post(commentUrl, params)

def testLogin():
	mineUrl = "https://www.douban.com/mine/"
	unLoginurlRedirect = "https://www.douban.com/accounts/login?redir=https%3A//www.douban.com/mine/"
	request = urllib2.Request(mineUrl)
	content = urllib2.urlopen(request).geturl()
	return unLoginurlRedirect != content

def _transcoding(data):
	if not data: return data
	result = None
	if type(data) == unicode:
		result = data
	elif type(data) == str:
		result = data.decode('utf-8')
	return result

def _get(url):
	request = urllib2.Request(url = url)
	response = urllib2.urlopen(request)
	data = response.read()
	return data

def _post(url, params, jsonfmt = False):
	if jsonfmt:
		request = urllib2.Request(url = url, data = json.dumps(params))
		request.add_header('ContentType', 'application/json; charset=UTF-8')
	else:
		request = urllib2.Request(url = url, data = urllib.urlencode(params))
	response = urllib2.urlopen(request)
	data = response.read()
	if jsonfmt: return json.loads(data, object_hook=_decode_dict)
	return data

def _decode_dict(data):
	rv = {}
	for key, value in data.iteritems():
		if isinstance(key, unicode):
			key = key.encode('utf-8')
		if isinstance(value, unicode):
			value = value.encode('utf-8')
		elif isinstance(value, list):
			value = _decode_list(value)
		elif isinstance(value, dict):
			value = _decode_dict(value)
		rv[key] = value
	return rv

def randomEmoticon():
    happy = ("_(┐「ε:)_","_(:3 」∠)_","(￣y▽￣)~*","・゜・(PД`q｡)・゜・","(ง •̀_•́)ง",
    "(•̀ᴗ•́)و ̑̑","ヽ(•̀ω•́ )ゝ","(,,• ₃ •,,)","(｡˘•ε•˘｡)","(=ﾟωﾟ)ﾉ","\(○’ω’○)","(´・ω・`)",
    "ヽ(･ω･｡)ﾉ","(。-`ω´-)","(´・ω・`)","(´・ω・)ﾉ","\(ﾉ･ω･)","  (♥ó㉨ò)ﾉ♡","(ó㉨ò)",
    "・㉨・","( ・◇・)？","ヽ(*´Д｀*)ﾉ","⁄(⁄ ⁄•⁄ω⁄•⁄ ⁄)⁄.","(´-ι_-｀)","ಠ౪ಠ","ಥ_ಥ",
    "(/≥▽≤/)","ヾ(o◕∀◕)ﾉ ヾ(o◕∀◕)ﾉ ヾ(o◕∀◕)ﾉ","\*★,°*:.☆\(￣▽￣)/$:*.°★*",
    "ヾ (o ° ω ° O ) ノ゙","╰(*°▽°*)╯ "," (｡◕ˇ∀ˇ◕）","o(*≧▽≦)ツ","≖‿≖✧",">ㅂ<","ˋ▽ˊ",
    "\(•ㅂ•)/♥","✪ε✪","✪υ✪","✪ω✪","눈_눈",",,Ծ‸Ծ,,","π__π","（/TДT)/","ʅ（´◔౪◔）ʃ","(｡☉౪ ⊙｡)",
    "o(*≧▽≦)ツ┏━┓拍桌狂笑"," (●'◡'●)ﾉ♥","<(▰˘◡˘▰)>","｡◕‿◕｡","(｡・`ω´･)","(♥◠‿◠)ﾉ","ʅ(‾◡◝) ",
    " (≖ ‿ ≖)✧","（´∀｀*)","（＾∀＾）","(o^∇^o)ﾉ","ヾ(=^▽^=)ノ","(*￣∇￣*)"," (*´∇｀*)","(*ﾟ▽ﾟ*)",
    "(｡･ω･)ﾉﾞ","(≡ω≡．)","(｀･ω･´)","(´･ω･｀)","(●´ω｀●)φ)")
    index = (int(random.random() * 1000))%len(happy)
    return happy[index]

def listenTopic():
	print '[*] 进入监听模式 ... 成功'
	while True:
		topicHtmlParser = GroupHtmlParser()
		html = _get("https://www.douban.com/group/")
		topicHtmlParser.feed(html)
		ck = topicHtmlParser.ck
		topicIds = topicHtmlParser.topicIds
		for topicId in topicIds:
			print(topicId)
			content = randomEmoticon()
			postDoubanComment(ck,content,topicId)
			time.sleep(1)
		time.sleep(10)

def main():
    if sys.stdout.encoding == 'cp936':
    	sys.stdout = UnicodeStreamFilter(sys.stdout)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
    urllib2.install_opener(opener)
    print('[*] 正在登陆豆瓣')
    opts, args = getopt.getopt(sys.argv[1:], "e:p:")
    email=""
    password=""
    for op, value in opts:
        if op == "-e":
            email = value
        elif op == "-p":
            password = value
    reload(sys)
    sys.setdefaultencoding('utf8')
    loginDouban(email,password)
    if testLogin() == True:
        print('[*] 登陆成功')
    else:
        print('[*] 登陆失败')
        exit()
    listenTopic()

if __name__ == '__main__':
    main()