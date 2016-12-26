#! /usr/bin/evn python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from jaccount import login
from utils import asp_params, EmptyCourse

import re
import logging

logger = logging.getLogger()

ELECT_URL = 'http://electsys.sjtu.edu.cn/edu/student/elect/'
LESSON_URL = 'http://electsys.sjtu.edu.cn/edu/lesson/'

class BasePage(object):
    def __init__(self, craker, text):
        self.text = text
        self.param.update(asp_params(self.text))
        self.craker = craker

    def proceed(self):
        return self.craker.post(self.url, data=self.param)

class InitPage(BasePage):
    url = ELECT_URL+'electwarning.aspx?xklc=2'
    def __init__(self, craker, text):
        self.param = {'CheckBox1': 'on', 'btnContinue': '继续'}
        super().__init__(craker, text)
        # self.url = ELECT_URL+'electwarning.aspx?xklc=1'

# class MainPage(BasePage):
#     def __init__(self, craker, text):
#         self.url = ELECT_URL+'speltyRequiredCourse.aspx'
#         self.param = {'SpeltyRequiredCourse1$btnQxsy': '抢选首页'}
#         super().__init__(craker, text)
#     # param.update(asp_params(self.sess.post(url, data=init_param).text))



class GrabPage(BasePage):
    def __init__(self, craker, text, param):
        self.url=ELECT_URL+'secondRoundFP.aspx?yxdm=&nj=2015&kcmk=-1&txkmk=-1&tskmk='
        self.param = param
        super().__init__(craker, text)

    def submit(self):
        submit_param = {'btnSubmit': '选课提交'}
        submit_param.update(asp_params(self.text))
        return self.craker.post(self.url, data=submit_param)
    # param = {'__EVENTTARGET': param}

class LessonPage(BasePage):
    def __init__(self, craker, text, url, course):
        self.url = url
        self.text = text
        self.param = {'myradiogroup': self.get_bsid(course),
                'LessonTime1$btnChoose': '选定此教师'}
        # if not self.param['myradiogroup']:
        super().__init__(craker, text)

    def get_bsid(self, course):
        soup = BeautifulSoup(self.text, 'html.parser')
        trs = soup.find_all('tr', {'class': re.compile('tdcolour\d')})
        courses = [LessonPageCourse(tr) for tr in trs]
        bsids = [c.bsid for c in courses if c.teacher == course.teacher and \
                c.remark == course.remark and course.time in c.time]
        if not bsids:
            raise EmptyCourse(self.url)
        # FIXME: Ask for user input if bsid is not determined.
        assert len(bsids) == 1
        return bsids[0]
        # if len(bsid) == 1:
        # for inp in soup.find_all('input', {'type': 'radio'}):
        #     if inp['value'] in course:
        #         return inp['value']

class LessonPageCourse(object):
    def __init__(self, tr):
        self.teacher = tr.find_all('td')[1].text.strip()
        self.time = tr.find_all('td')[9].text.strip()
        self.remark = tr.find_all('td')[10].text.strip()
        self.bsid = tr.input['value']
