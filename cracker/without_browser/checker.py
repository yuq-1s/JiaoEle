import requests
import json
from .sdtMain import Cracker, LESSON_URL
from .utils import asp_params
from urllib.parse import urlencode
from logging import getLogger

logger = getLogger(__name__)

# courses = [{'cid': 'PO039', 'property': '选修', 

RENXUAN_URL=ELECT_URL+'viewLessonArrange.aspx?xklx=%e9%80%89%e4%bf%ae&redirectForm=outSpeltyEp.aspx&kcmk=-1'

# 'http://electsys.sjtu.edu.cn/edu/student/elect/electSubmit.aspx'
class Checker(Cracker):
    filename = 'data/courses.json'
    def __init__(self, user, passwd):
        with open(filename, 'r') as f:
            self.courses = json.load(f)
        super().__init__(user, passwd)

    def check(self):
        return [c for c in self.courses if self.is_full(course)]

    def is_full(self, course):
        param = {'myradiogroup': course['bsid'],
                'LessonTime1$btnChoose': '选定此教师'}
        param.update(asp_params(course['text']))
        resp = self.sess.post(url=course['url'], data=param,
            allow_redirects=False)
        if 'message=' in resp.text:
            return False
        else:
            return True


        # if course['property'] == '选修':
        #     url = RENXUAN_URL
        # else:
        # # property2page = {'必修': 'speltyRequiredCourse.aspx', 
        # #         '通识': 'speltyCommonCourse.aspx',
        # #         '限选': 'speltyLimitedCourse.aspx',
        # #         '选修': 'outSpeltyEp.aspx'}
        #     query = {'kcdm': course['cid'],
        #             'xklx': course['property'], 
        #             # 'redirectForm': property2page(course['property']),
        #             'nj': course['grade'],
        #             'kcmk': '-1',
        #             'txkmk': '-1'
        #             }
        #     url=LESSON_URL+'viewLessonArrange.aspx?'+urlencode(query)
