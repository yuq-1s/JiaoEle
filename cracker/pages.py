#! /usr/bin/evn python3
# -*- coding: utf-8 -*-

from jaccount import login
from utils import asp_params

ELECT_URL = 'http://electsys.sjtu.edu.cn/edu/student/elect/'
LESSON_URL = 'http://electsys.sjtu.edu.cn/edu/lesson/'

class BasePage(object):
    def __init__(self, craker, text):
        self.text = text
        self.param.update(asp_params(self.text))
        self.craker = craker

    # def update_sess(self, sess):
    #     self.craker.update_sess()

    def proceed(self):
        # self.craker.post(self.url, data=self.param)
        # resp = self.craker.post(self.url, data=self.param)
        # self.craker.handle_outdate(resp)
        # self.craker.handle_message(resp)
        return self.craker.post(self.url, data=self.param)

class InitPage(BasePage):
    url = ELECT_URL+'electwarning.aspx?xklc=1'
    def __init__(self, craker, text):
        self.param = {'CheckBox1': 'on', 'btnContinue': '继续'}
        super().__init__(craker, text)
        # self.url = ELECT_URL+'electwarning.aspx?xklc=1'

class MainPage(BasePage):
    def __init__(self, craker, text):
        self.url = ELECT_URL+'speltyRequiredCourse.aspx'
        self.param = {'SpeltyRequiredCourse1$btnQxsy': '抢选首页'}
        super().__init__(craker, text)
    # param.update(asp_params(self.sess.post(url, data=init_param).text))



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
    def __init__(self, craker, text, url, bsids):
        self.url = url
        self.text = text
        self.param = {'myradiogroup': self.get_bsid(bsids),
                'LessonTime1$btnChoose': '选定此教师'}
        if not self.param['myradiogroup']:
            raise EmptyCourse(self.url)
        super().__init__(craker, text)

    def get_bsid(self, possible_bsids):
        soup = BeautifulSoup(self.text, 'html.parser')
        for inp in soup.find_all('input', {'type': 'radio'}):
            if inp['value'] in possible_bsids:
                return inp['value']

