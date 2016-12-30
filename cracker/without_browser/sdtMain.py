#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# TODO:
# 1. store cookies
# 2. auto check if course full
# 3. select by {property name teacher time}.
# 4. input json file

from pdb import set_trace
from bs4 import BeautifulSoup
import requests
from logging import getLogger, StreamHandler, Formatter, DEBUG, FileHandler,INFO
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

formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = StreamHandler(stdout)
ch.setLevel(INFO)
ch.setFormatter(formatter)

LOG_PATHNAME = '/home/yuq/Documents/projects/python/elecysys/log/'
LOG_FILENAME = sys.argv[1]+'-qiangke'
fh = FileHandler('{}/{}.log'.format(LOG_PATHNAME, LOG_FILENAME))
fh.setLevel(INFO)
fh.setFormatter(formatter)

logger.addHandler(ch)
logger.addHandler(fh)


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
        logger.info('Trying to login...')
        self.sess = login(self.user, self.passwd)
        logger.info('Login succeeded.')
        self.refresh()

    def post(self, *args, **kw):
        resp = self.sess.post(*args, **kw)
        for cnt in itertools.count():
            try:
                resp.raise_for_status()
                self.handle_outdate(resp)
                self.handle_message(resp)
            except (SessionOutdated, MessageError) as e:
                resp = self.sess.post(*args, **kw)
                logger.debug('The %d times post failed' % cnt)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 500:
                    raise e
                resp = self.sess.post(*args, **kw)
                logger.debug('The %d times post failed' % cnt)
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
            raise MessageError(message)
        except IndexError:
            pass

    @abstractmethod
    def refresh(self):
        pass

class Master(Cracker):
    def _get_failed_courses(self):
        soup = BeautifulSoup(self.qxresp.text, 'html.parser')

        failed_trs = [tag.parent.parent for tag in \
            soup.find_all('font', {'color': 'Red'}) \
            if tag.parent.parent.a and tag.text == '否']
        return [Course(tr) for tr in failed_trs]


    def refresh(self):
        logger.info('Refreshing...')
        self.initpage = InitPage(self, self.sess.get(InitPage.url).text)
        self.qxresp = self.initpage.proceed()
        self.courses = self._get_failed_courses()
        self.names = [c.name for c in self.courses]
        self.cid2name = {c.cid: c.name for c in self.courses}
        logger.info('Refresh complete.')

    def run(self):
        for course in self.courses:
            Worker(self, course).start()

class Worker(Cracker, Thread):
    def __init__(self, master, course):
        self.master = master
        self.course = course
        super().__init__(master.user, master.passwd)

    def refresh(self):
        logger.info('%s refreshing...'% self.course.name)
        self.initpage = InitPage(self, self.sess.get(InitPage.url).text)
        self.qxresp = self.initpage.proceed()
        logger.info('Refresh complete.')

    def handle_message(self, resp):
        logger.debug(self.course.name)
        super().handle_message(resp)

    def run(self):
        param = self.course.params
        self.grabpage = GrabPage(self, self.qxresp.text, param)
        lesson_resp = self.grabpage.proceed()
        try:
            self.lessonpage = LessonPage(self, lesson_resp.text, 
                    lesson_resp.url, self.course)
        except EmptyCourse as e:
            logger.error('Encounter empty course: %s' % e)
            return

        logger.info('Grabbing course %s...' % self.course.name)

        # FIXME: This condition may not work when multi-threading
        while self.course.name in self.master.names: # Course not got
            try:
                self.lessonpage.proceed()
                submit_response = self.grabpage.submit()
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

    # def post(self, *args, **kw):
    #     try:
    #         self.sess.post(self.grabpage.url, self.grabpage.param)
    #         self.sess.post(self.lessonpage.url, self.lessonpage.para)
    #     except AttributeError:
    #         pass
    #     return super().post(*args, **kw)


if __name__ == '__main__':
    Master(sys.argv[1], sys.argv[2]).run()
