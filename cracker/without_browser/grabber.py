#! /usr/bin/env ipython3

import itertools
import json
import sys
import concurrent.futures
import queue

from pdb import set_trace
from abc import ABCMeta, abstractmethod
from queue import Queue
from threading import Lock, Thread
from utils import asp_params
from jaccount import login
from logging import getLogger, DEBUG, INFO, StreamHandler, FileHandler,Formatter
from urllib.parse import urlencode

ELECT_URL='http://electsys.sjtu.edu.cn/edu/student/elect/'
LESSON_URL='http://electsys.sjtu.edu.cn/edu/lesson/viewLessonArrange.aspx'
# 向任选课post可以选所有课程
COURSE_URL=LESSON_URL+'?&xklx=&redirectForm=outSpeltyEp.aspx&kcmk=-1'
SUBMIT_URL=ELECT_URL+'electSubmit.aspx'
REMOVE_URL=ELECT_URL+'removeRecommandLesson.aspx'
REMOVE_QUERY={'redirectForm': 'removeLessonFast.aspx'}
MAIN_URL=ELECT_URL+'electcheck.aspx?xklc=2'

logger = getLogger(__name__)

# TODO: Check confict courses
# TODO: Cancle course utility
class CourseGrabber(Thread):
    def __init__(self, master, filename=None, courses=[]):
        super().__init__()
        self.cancel_lock = Lock()
        self.canceled = True
        self.master = master
        self.cqueue = Queue()

        if filename:
            with open(filename) as f:
                courses = json.load(f)

        for course in courses:
            self.add_course(course)

    # TODO: Handle outdated session 
    # TODO: Check course got.
    def select_course(self, course):
        # Select target course
        self.master.main_sess.post(url=COURSE_URL,
                data=course['param'], allow_redirects=False)
        # Submit
        self.master.main_sess.head(SUBMIT_URL)
        logger.info('Successfully got course %s'% course['name'])

    def add_course(self, course):
        # param = {'myradiogroup': course['bsid'],
        #     'LessonTime1$btnChoose': '选定此教师'}
        # with open('pages/'+course['cid']) as f:
        #     param.update(asp_params(f.read()))
        # course['param'] = param
        self.cqueue.put(course)

    def run(self):
        with self.cancel_lock:
            self.canceled = False

        while True:
            with self.cancel_lock:
                if self.canceled:
                    return
            try:
                course = self.cqueue.get(timeout=5)

                if self.is_full(course):
                    # logger.debug('course full.')
                    self.cqueue.put(course)
                else:
                    self.select_course(course)
            except queue.Empty:
                logger.info('All courses successfully selected')
                self.do_quit()
                return

        # with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        #     executor.submit(self.run_workers)

    def do_quit(self):
        with self.cqueue.mutex:
            self.cqueue.queue.clear()

        with self.cancel_lock:
            self.canceled = True

    def is_full(self, course):
        if 'messagePage' in self.master.sess.post(url=COURSE_URL,
                data=course['param'], allow_redirects=False).text:
            return True
        else:
            return False

class CourseReplacer(CourseGrabber):
    # HACK: select_course takes 1 positional parameter.
    # TODO: Check whether succeeded.
    def select_course(self, course_pair):
        target, original = course_pair
        # Test if master.main_sess can submit
        # TODO: Update master.main_sess every some minutes.
        if 'messagePage' in self.master.main_sess.head(SUBMIT_URL).headers['Location']:
            logger.error('Session outdated. refreshing...')
            self.master.refresh_main_sess()

        remove_query = {'bsid': original['bsid']}
        remove_query.update(REMOVE_QUERY)
        # Select target course
        resp = self.master.main_sess.post(url=COURSE_URL,
                data=target['param'], allow_redirects=False)
        # if target['bsid'] in resp.text: # successfully got target class
        self.master.main_sess.head(REMOVE_URL+'?'+urlencode(remove_query))
        # Submit
        self.master.main_sess.head(SUBMIT_URL)

        print('Submit %s complete. Checking whether succeeded...' % target['name'])
        assert target['bsid'] in self.master.main_sess.get(MAIN_URL).text, \
            'Sadly, We lost course %s when trying to get %s'\
            % (target['name'], original['name'])
        print('Grabbing %s succeeded!' % target['name'])


    def is_full(self, course):
        if 'messagePage' in self.master.sess.post(url=COURSE_URL,
                data=course[0]['param'], allow_redirects=False).text:
            return True
        else:
            return False
            logger.info('Successfully got course %s'% target['name'])



    # def is_selected(self, course):
    #     if course['name'] in self.master_sess.get(\
    #             ELECT_URL+'secondRoundFP.aspx').text:
    #         return True
    #     else:
    #         return False

        # if self.is_selected(course):
        #     logger.info('Successfully got %s' % course['name'])
        # else:
        #     self.cqueue.put(course)

# class CourseTable(Queue):
#     def __init__(self):
#         super().__init__()
#         self.courses = set()

#     def put(self, course):
#         self.courses.add(course)
#         if any([are_overlap(c, course) for c in self.courses]):
#             raise ConfictCourse(course)
#         else:
#             super().put(course)

#     def remove(self, course):
#         self.courses.remove(course)
#         # clear the queue


if __name__ == '__main__':
    CourseGrabber(sys.argv[1], sys.argv[2], courses=[{'cid': 'HU902', 
        'bsid': '381911',  'name': '爱'},
        {'cid': 'CS902', 'bsid': '381831', 'name': '计算机'}]).run()

