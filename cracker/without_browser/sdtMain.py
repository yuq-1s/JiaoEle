#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from pdb import set_trace
from bs4 import BeautifulSoup
import requests
from logging import getLogger, StreamHandler, Formatter, DEBUG
from itertools import count
from functools import wraps
from sys import stdout
from urllib.parse import urlencode, urlparse, unquote, parse_qs
from lxml import etree
from time import sleep
from threading import Thread
from pages import InitPage, GrabPage, LessonPage
from utils import MessageError, SessionOutdated, EmptyCourse
from jaccount import login
from abc import ABCMeta, abstractmethod

from concurrent.futures import ThreadPoolExecutor
import itertools
import re
import sys

# TODO:
#   1. Try to grab courses directly.(not step by step from main page)
#   2. Every worker uses its own requests.Session
#   3. Global permission to post if multiple sessions don't work

# When in main page (aka path /)
ELECT_URL = 'http://electsys.sjtu.edu.cn/edu/student/elect/'
LESSON_URL = 'http://electsys.sjtu.edu.cn/edu/lesson/'
# MAIN_PAGE_URL = ELECT_URL+'sltFromRcommandTbl.aspx'


logger = getLogger(__name__)
logger.setLevel(DEBUG)

ch = StreamHandler(stdout)
ch.setLevel(DEBUG)
formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class Course(object):
    def __init__(self, tr):
        tds = tr.find_all('td')
        self.params = {'__EVENTTARGET': tr.a.attrs['href'].split("'")[1]}
        self.teacher = tds[3].text.strip()
        self.time = tds[4].text.strip()
        self.remark = tds[5].text.strip()
        self.name = tds[0].text.strip()
        self.cid = re.search('[A-Z]{2}\d{3}', tds[1].text).group(0)

class Cracker(metaclass=ABCMeta):
    def __init__(self, user, passwd):
        super().__init__()
        self.user = user
        self.passwd = passwd
        logger.debug('Login succeeded.')
        self.sess = login(self.user, self.passwd)
        logger.debug('Login succeeded.')
        self.refresh()

    def post(self, *args, **kw):
        resp = self.sess.post(*args, **kw)
        for cnt in itertools.count():
            try:
                resp.raise_for_status()
                self.handle_outdate(resp)
                self.handle_message(resp)
            except (SessionOutdated, MessageError, requests.exceptions.HTTPError):
                logger.debug('The %d times post failed' % cnt)
                resp = self.sess.post(*args, **kw)
            else:
                return resp


    def handle_outdate(self, resp):
        if 'outTimePage.aspx' in resp.url:
            logger.warn('Session outdated. Recovering...')
            self.sess = login(self.user, self.passwd)
            self.refresh()
            raise SessionOutdated


    def handle_message(self, resp):
        try:
            message = unquote(resp.url.split('message=')[1])
            logger.debug(message)
            if '刷新' in message:
                sleep(1)
            elif message == '已提交，请等待教务处的微调结果！':
                return
            raise MessageError
        except IndexError:
            pass

    @abstractmethod
    def refresh(self):
        logger.error('This method is a stub. Please write it in the children.')
        sys.exit(-1)

class Master(Cracker):
    # def __init__(self, user, passwd):
    #     super().__init__(user, passwd)
    #     self.user = user
    #     self.passwd = passwd
    #     # self.view_param = param
    #     logger.debug('Login succeeded.')
    #     self.sess = login(self.user, self.passwd)
    #     logger.debug('Login succeeded.')
    #     self.refresh()

    def _get_failed_courses(self):
        soup = BeautifulSoup(self.qxresp.text, 'html.parser')

        failed_trs = [tag.parent.parent for tag in \
            soup.find_all('font', {'color': 'Red'}) \
            if tag.parent.parent.a and tag.text == '否']
        return [Course(tr) for tr in failed_trs]


    def refresh(self):
        logger.debug('Refreshing...')
        self.initpage = InitPage(self, self.sess.get(InitPage.url).text)
        self.qxresp = self.initpage.proceed()
        self.courses = self._get_failed_courses()
        self.names = [c.name for c in self.courses]
        self.cid2name = {c.cid: c.name for c in self.courses}
        logger.debug('Refresh complete.')

    def run(self):
        for course in self.courses:
            Worker(self, course).start()

class Worker(Cracker, Thread):
    def __init__(self, master, course):
        self.master = master
        self.course = course
        super().__init__(master.user, master.passwd)

    def refresh(self):
        logger.debug('%s refreshing...'% self.course.name)
        self.initpage = InitPage(self, self.sess.get(InitPage.url).text)
        self.qxresp = self.initpage.proceed()
        logger.debug('Refresh complete.')

    def handle_message(self, resp):
        logger.debug(self.course.name)
        super().handle_message(resp)

    def run(self):
        param = self.course.params
        grabpage = GrabPage(self, self.qxresp.text, param)
        lesson_resp = grabpage.proceed()
        try:
            lessonpage = LessonPage(self, lesson_resp.text, 
                    lesson_resp.url, self.course)
        except EmptyCourse as e:
            logger.error('Encounter empty course: %s' % e)
            return

        logger.info('Grabbing course %s...' % self.course.name)

        # FIXME: This condition may not work when multi-threading
        while self.course.name in self.master.names: # Course not got
            try:
                lessonpage.proceed()
                submit_response = grabpage.submit()
                assert 'successful.aspx' in submit_response.url, 'Submit failed'
                break
            except ConnectionError as e:
                sleep(5)
                logger.error(e)
            except AssertionError as e:
                if str(e) == 'Submit failed':
                    logger.error('Redirected to %s after course available'%resp.url)
                    logger.error('Why cannot submit?')
            else:
                self.master.refresh()

        logger.info('Successfully got %s.' % self.course.name)


class Runner(Thread):
    def __init__(self, cracker, course):
        super().__init__()
        # self.grabpage = grabpage
        # self.lessonpage = lessonpage
        self.cracker = cracker
        self.course = course

    def run(self):
        param = self.course.params
        grabpage = GrabPage(self.cracker, self.cracker.qxresp.text, param)
        lesson_resp = grabpage.proceed()
        try:
            lessonpage = LessonPage(self.cracker, lesson_resp.text, 
                    lesson_resp.url, self.course)
        except EmptyCourse as e:
            logger.error('Encounter empty course: %s' % e)
            return

        logger.info('Grabbing course %s...' % self.course.name)

        while self.course.name in self.cracker.names: # Course not got
            try:
                lessonpage.proceed()
                submit_response = grabpage.submit()
                assert 'successful.aspx' in submit_response.url, 'Submit failed'
                break
            except ConnectionError as e:
                sleep(5)
                logger.error(e)
            except AssertionError as e:
                if str(e) == 'Submit failed':
                    logger.error('Redirected to %s after course available'%resp.url)
                    logger.error('Why cannot submit?')
            else:
                self.cracker.refresh()

        logger.info('Successfully got %s.' % self.course.name)

#         logger.info('Grabbing course %s...'%self.param['myradiogroup'])
#         for cnt in itertools.count():
#             try:
#                 if 'message=' not in cracker.lessonpage.proceed().url:
#                     # if '/secondRoundFP.aspx' in resp.url:
#                     resp = cracker.grabpage.submit()
#                     if not 'successful.aspx' in resp.url:
#                         logger.error('Redirected to %s after course available'%resp.url)
#                         # respi = self.cracker.initpage.proceed()
#                         # respm = self.cracker.mainpage.proceed()
#                         # respa = self.cracker.grabpage.proceed()
#                         logger.error('Why cannot submit?')
#                         # raise ResetException
#                     else:
#                         logger.error('Successfully got %s lesson.'%
#                                 cracker.lessonpage.url)
#                         return
#             except ConnectionError as e:
#                 sleep(5)
#                 logger.error(e)
#             logger.error('Resetting the %d times'%cnt)


#         for param in params:
#             try:
#                 Runner(self.grabpage, self.lessonpage, self).run()
#             except EmptyCourse as e:
#                 logger.error('Empty course: %s'%e)

# class LessonPage(BasePage):
#     url = ELECT_URL+

# '%e4%bd%a0%e7%9a%84%e5%ad%a6%e5%88%86%e8%b6%85%e5%87%ba%e8%a6%81%e6%b1%82%ef%bc%8c%e8%af%b7%e6%a3%80%e6%9f%a5%ef%bc%81'

if __name__ == '__main__':
    # test_course = course(**{'cid': 'PS900', 'bsid': '456723', 'xyid': 'ba231'})
    # qiangke(requests.Session(), test_course)
    # main_page(login('zxdewr', 'pypy11u'))
    # sess = login('zxdewr', 'p1ptess')
    # init(sess)

    Master(sys.argv[1], sys.argv[2]).run()

    # def _get_failed_courses(self):
    #     soup = BeautifulSoup(self.qxresp.text, 'html.parser')

    #     failed_trs = [tag.parent.parent for tag in \
    #         soup.find_all('font', {'color': 'Red'}) \
    #         if tag.parent.parent.a and tag.text == '否']
    #     return [Course(tr) for tr in failed_trs]


    # def refresh(self):
    #     logger.debug('Refreshing...')
    #     self.initpage = InitPage(self, self.sess.get(InitPage.url).text)
    #     # self.mainpage = MainPage(self, self.initpage.proceed().text)
    #     self.qxresp = self.initpage.proceed()
    #     # self.bsids = re.findall('bsid=(\d{6})', self.qxresp.text)
    #     self.courses = self._get_failed_courses()
    #     self.names = [c.name for c in self.courses]
    #     self.cid2name = {c.cid: c.name for c in self.courses}
    #     logger.debug('Refresh complete.')

    # def _crack(self, course):
    #     param = course.params
    #     grabpage = GrabPage(self, self.qxresp.text, param)
    #     lesson_resp = grabpage.proceed()
    #     try:
    #         lessonpage = LessonPage(self, lesson_resp.text, 
    #                 lesson_resp.url, course)
    #     except EmptyCourse as e:
    #         logger.error('Encounter empty course: %s' % e)
    #         return

    #     logger.info('Grabbing course %s...' % course.name)

    #     while course.name in self.names: # Course not got
    #         try:
    #             lessonpage.proceed()
    #             submit_response = grabpage.submit()
    #             assert 'successful.aspx' in submit_response.url, 'Submit failed'
    #             break
    #         except ConnectionError as e:
    #             sleep(5)
    #             logger.error(e)
    #         except AssertionError as e:
    #             if str(e) == 'Submit failed':
    #                 logger.error('Redirected to %s after course available'%resp.url)
    #                 logger.error('Why cannot submit?')
    #         else:
    #             self.refresh()

    #     logger.info('Successfully got %s.' % course.name)

        # with ThreadPoolExecutor(max_workers=len(self.courses)) as executor:
        #     executor.map(self._crack, self.courses)
