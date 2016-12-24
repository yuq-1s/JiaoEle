#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from pdb import set_trace
from bs4 import BeautifulSoup
import requests
from logging import getLogger, StreamHandler, Formatter, DEBUG
from itertools import count
from functools import wraps
from sys import stdout
from urllib.parse import urlencode, urlparse, unquote
from lxml import etree
from time import sleep
from threading import Thread
from pages import InitPage, MainPage, GrabPage, LessonPage
from utils import MessageError, SessionOutdated, EmptyCourse
from jaccount import login

import itertools
import re
# TODO:
#   1. Try to grab courses directly.(not step by step from main page)

# When in main page (aka path /)
ELECT_URL = 'http://electsys.sjtu.edu.cn/edu/student/elect/'
LESSON_URL = 'http://electsys.sjtu.edu.cn/edu/lesson/'
# MAIN_PAGE_URL = ELECT_URL+'sltFromRcommandTbl.aspx'


logger = getLogger(__name__)

# ch = StreamHandler(stdout)
# ch.setLevel(DEBUG)
# formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# ch.setFormatter(formatter)
# logger.addHandler(ch)



class Runner(Thread):
    def __init__(self, grabpage, lessonpage, cracker):
        super().__init__()
        self.grabpage = grabpage
        self.lessonpage = lessonpage
        self.cracker = cracker

    def run(self):
        for cnt in itertools.count():
            try:
                if 'message=' not in self.lessonpage.proceed().url:
                    # if '/secondRoundFP.aspx' in resp.url:
                    resp = self.grabpage.submit()
                    if not 'successful.aspx' in resp.url:
                        logger.error(resp.url)
                        respi = self.cracker.initpage.proceed()
                        respm = self.cracker.mainpage.proceed()
                        respa = self.cracker.grabpage.proceed()
                        logger.error('Why cannot submit?')
                        # raise ResetException
                    else:
                        logger.error('Successfully got %s lesson.'%
                                self.lessonpage.url)
                        return
            except ConnectionError as e:
                sleep(5)
                logger.error(e)


class Cracker(object):
    def __init__(self, user, passwd):
        super().__init__()
        self.user = user
        self.passwd = passwd
        # self.view_param = param
        self.sess = login(self.user, self.passwd)

    def crack(self):
        self.initpage = InitPage(self, self.sess.get(InitPage.url).text)
        self.mainpage = MainPage(self, self.initpage.proceed().text)
        qxresp = self.mainpage.proceed()
        bsids = re.findall('bsid=(\d{6})', qxresp.text)
        params = [{'__EVENTTARGET': tag.parent.parent.a.attrs['href'].split("'")[1]} 
                for tag in BeautifulSoup(qxresp.text,'html.parser').find_all('font', {'color': 'Red'}) \
                        if tag.parent.parent.a and tag.text == '否']

        for param in params:
            try:
                self.grabpage = GrabPage(self, qxresp.text, param)
                lesson_resp = self.grabpage.proceed()
                self.lessonpage = LessonPage(self, lesson_resp.text, 
                        lesson_resp.url, bsids)
                Runner(self.grabpage, self.lessonpage, self).run()
            except EmptyCourse as e:
                logger.error(e)

    def post(self, *args, **kw):
        resp = self.sess.post(*args, **kw)
        while True:
            try:
                self.handle_outdate(resp)
                self.handle_message(resp)
            except SessionOutdated:
                self.sess = login(self.user, self.passwd)
                # FIXME: initpage needed?
                self.initpage = InitPage(self, self.sess.get(InitPage.url).text)
                resp = self.sess.post(*args, **kw)
            except MessageError as e:
                resp = self.sess.post(*args, **kw)
            else:
                return resp


    def handle_outdate(self, resp):
        if 'outTimePage.aspx' in resp.url:
            self.sess = login(self.user, self.passwd)
            raise SessionOutdated
        # return resp


    def handle_message(self, resp):
        try:
            message = unquote(resp.url.split('message=')[1])
            logger.info(message)
            if '刷新' in message:
                sleep(1)
            elif message == '该课该时间段人数已满！':
                logger.debug(message)
                # raise CourseFull(message)
            raise MessageError
        except IndexError:
            pass



# class LessonPage(BasePage):
#     url = ELECT_URL+

# '%e4%bd%a0%e7%9a%84%e5%ad%a6%e5%88%86%e8%b6%85%e5%87%ba%e8%a6%81%e6%b1%82%ef%bc%8c%e8%af%b7%e6%a3%80%e6%9f%a5%ef%bc%81'

if __name__ == '__main__':
    # test_course = course(**{'cid': 'PS900', 'bsid': '456723', 'xyid': 'ba231'})
    # qiangke(requests.Session(), test_course)
    # main_page(login('zxdewr', 'pypy11u'))
    # sess = login('zxdewr', 'p1ptess')
    # init(sess)

    Cracker('zxdewr', 'ca1l6ack').crack()
