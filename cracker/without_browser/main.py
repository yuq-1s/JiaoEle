#! /usr/bin/python3
# -*- coding: utf-8 -*-
# import jaccount, sdtMain

from urllib.parse import unquote, urlparse, parse_qs
from pathlib import Path
from logging import getLogger
from pdb import set_trace
from jaccount import login
from time import sleep
from concurrent.futures import ThreadPoolExecutor
from current import parse_current
from prettytable import PrettyTable
from grabber import CourseGrabber, CourseReplacer
from utils import asp_params, get_logger, ELECT_URL, MAIN_URL, REMOVE_URL
from utils import SUBMIT_URL
from courses import are_overlap, contains
from tqdm import tqdm

import concurrent.futures
import termcolor
import xpinyin
import traceback
import logging
import copy
import time
import json
import os
import sys
import re
import cmd

logger = get_logger(__name__)

def load_file(filename):
        with open(filename, 'r') as f:
            return json.load(f)

# TODO: Exception handling
# TODO: def get_grabbing: print out courses the software is grabbing.
# TODO: Cancel / Pause course grabbing
# TODO: Multiple modes: 1. Only query; 2. Query with browser grabbing 3. ...
# TODO: Print course type
# TODO: Notify user newly availble courses in real time.
# TODO: Reset after unknown exception.
# FIXME: This version assumes all courses are submited and nothing conflicts.
class Main(cmd.Cmd):
    CURRENT_PATH = 'data/current.json'
    COURSES_PATH = 'data/tongshi.json'
    EXPIRE_SEC = 900
    intro = '\n Here is the evil software to help you select courses.\n Have fun (~˘▾˘)~'
    prompt = '>> '

    def __init__(self):
        print('Initializing...')
        super().__init__()
        self.py = xpinyin.Pinyin()
        try:
            self.user = sys.argv[1]
            self.passwd = sys.argv[2]
        except IndexError:
            self.user = input('Jaccount username: ')
            self.passwd = input('Jaccount password: ')
        print('Trying to login...')
        self.sess = login(self.user, self.passwd)
        self.sess.head(MAIN_URL)
        print('Login succeeded.')

        # FIXME: parse_current fails before 选课 begin.
        self.__update_current()
        print('Loading course file...')
        self.courses = load_file(self.COURSES_PATH)

        self.grabber = CourseGrabber(self)
        self.replacer = CourseReplacer(self)

        for course in tqdm(self.courses):
            param = {'myradiogroup': course['bsid'],
                'LessonTime1$btnChoose': '选定此教师'}
            with open('pages/'+course['cid']) as f:
                param.update(asp_params(f.read()))
            course['param'] = param
        print('Initializing succeeded!')

    def preloop(self):
        print(termcolor.colored('Warning: This version assumes all courses are '
        'submited and nothing conflicts.', 'yellow'))

    def refresh_main_sess(self):
        self.main_sess = login(self.user, self.passwd)
        self.main_sess.head(MAIN_URL)

    @staticmethod
    def parse_period(raw):
        odd = []
        even = []
        for period in raw.split(';'):
            try:
                r=re.match('\'?\"?(\d)\s+(\d+)\s+(\d+)(?:\s+(\d+)\s+(\d+))?(\s+[oe]{1,2})?\'?\"?',period).groups()
                if len(r) != 6: continue
                if not any(r): continue
                queried_time = {}
                queried_time['wbegin'] = r[3] if r[3] else 1
                queried_time['wend'] = r[4] if r[4] else 16
                # ret['wbegin'] = r[5] if r[5] else 'oe'
                assert r[0] and 1 <= int(r[0]) <= 7, 'Weekday must in range 1-7'
                assert r[1] and 1 <= int(r[1]) <= 14, 'Course period must be in range 1-14'
                assert r[2] and 1 <= int(r[2]) <= 14, 'Course period must be in range 1-14'
                assert 1 <= int(queried_time['wbegin']) <= 16, 'Week period must in range 1-16'
                assert 1 <= int(queried_time['wend']) <= 16, 'Week peroid must in range 1-16'
                queried_time['cbegin'], queried_time['cend']=min(int(r[1]), int(r[2])), max(int(r[1]), int(r[2]))
                queried_time['weekday'] = '日一二三四五六'[int(r[0])]
                # queried_time['cbegin'] = int(r[1])
                # queried_time['cend'] = int(r[2])
                parity = r[5] if r[5] else 'oe'

                if 'o' in parity:
                    if queried_time not in odd:
                        odd.append(queried_time)
                if 'e' in parity:
                    if queried_time not in even:
                        even.append(queried_time)

            except AssertionError as e:
                logger.warn(e)
                logger.warn('Ignored: %s', period)
            except AttributeError as e:
                logger.warn(e)
                logger.warn('Ignored: %s', period)
                logger.warn('Invalid syntax')

        return {'odd_week': odd, 'even_week': even}


    def __to_letter(self, s):
        ''' 汉语拼音 -> hypy
        '''
        return re.sub(r'[^\w\s]', '', self.py.get_initials(s, '')).lower()


    # FIXME: Courses with the same initial letters are not distinguished.
    def do_qname(self, arg):
        ''' Print out courses based on name query.
            Support pinyin abbreviation.
            Example: >> qname ty4
                    for query of 体育（4）
        '''
        self.print_courses([c for c in self.courses \
            if self.__to_letter(c['name']) == arg or c['name'] == arg])

    def complete_qname(self, text, line, begidx, endidx):
        ''' Auto-completion utility for qname.
            With support for pinyin.
        '''
        if not text:
            completions = self.courses[:]
        else:
            completions = [c['name'] for c in self.courses 
                    if self.__to_letter(c['name']).startswith(text)]

        return [c['name'] for c in self.courses if \
                self.__to_letter(c['name']).startswith(self.__to_letter(text)) \
                ] if text else self.courses

    def do_ls(self, _):
        ''' Print out all courses loaded from the resource file.'''
        self.print_courses(self.courses)

    def do_qavai(self, _):
        ''' Print out all avalible courses not overlapping with your currently
            selected courses
        '''
        self.print_courses(c for c in self.courses if self.can_select(c))
        # self.print_courses(c for c in self.courses for curr in self.current \
        #         if not are_overlap(c, curr))
        # print({c['name'] for c in self.courses for curr in self.current \
        #         if not are_overlap(c, curr)})

        # for course in self.courses:
        #     for curr in self.current:
        #         if not are_overlap(course, curr):
        #             print(course['name'])

    def non_overlap_by_time(self, raw):
        ''' Usage: <2, 1, 3[, 1, 8][, 'o']>[;...]
            @return: Course names that do not overlap with any queried period,
                    without considering current selected courses.
        '''

        queried = Main.parse_period(raw)
        if not queried['odd_week'] and not queried['even_week']:
            logger.warn('Invalid input, nothing to query.')
            # return set()
        return {c['name'] for c in self.courses if not are_overlap(c, queried)}

    def do_period(self, raw):
        ''' Return courses contained in your queries

            Example: >> period '2 9 10 o;4 7 8 1 8 e'
                    will show courses contained in the union of 
                    Tuesday from 9 to 10 节 from 1 to 16 odd weeks and 
                    Thursday from 7 to 8 节 from 1 to 8 even weeks.
        '''
        queried = Main.parse_period(raw)
        if not queried['odd_week'] and not queried['even_week']:
            logger.warn('Invalid input, nothing to query.')
            # print(set())

        self.print_courses([c for c in self.courses if contains(queried, c)])

    # TODO: List Grabbing results.
    def do_bye(self, arg):
        ''' Exit.
        '''
        if not self.grabber.canceled or not self.replacer.canceled:
            print()
            if input('Quiting will abort course grabbing. Confirm? Y/[N]') \
                .lower() != 'y':
                    return

        self.grabber.canceled = True
        self.replacer.canceled = True
        print('Bye')
        return True

    def do_EOF(self, _):
        ''' Exit.
        '''
        while True:
            try:
                inp = input('quit now? y/[n].')
                if inp == 'y':
                    self.do_bye(_)
                    return True

                if inp == 'n':
                    return False
            except EOFError:
                self.do_bye(_)
                return True

    def get_overlap(self, course):
        for curr in self.current:
            if are_overlap(curr, course):
                yield curr

    def do_grab(self, arg):
        try:
            self.main_sess
        except AttributeError:
            self.refresh_main_sess()

        input_courses = [c for bsid in arg.split(',') for c in self.courses \
                if c['bsid'] == re.search('\d{6}', bsid).group()]
        courses_to_replace = [c for c in input_courses \
                if not self.can_select(c)]
        courses_to_grab = [c for c in input_courses if c not in courses_to_replace]
        replace_pairs = [(c, next(self.get_overlap(c))) for c in courses_to_replace]

        if courses_to_replace:
            self.print_courses((cp[0] for cp in replace_pairs))
            if input('These are conflict with your currently selected courses. '
            'Do you want to replace original ones with these? Y/[N]')\
                    .lower() != 'y':
                        print('Grabbing canceled.')
                        return

        if courses_to_grab:
            self.print_courses(courses_to_grab)
            if input('Ready to grab these courses. Confirm? Y/[N]: ')\
                    .lower() != 'y':
                        print('Grabbing canceled.')
                        return

        for course in courses_to_grab:
            self.grabber.add_course(course)
        if courses_to_grab and not self.grabber.is_alive():
            self.grabber.start()

        for course_pair in replace_pairs:
            self.replacer.add_course(course_pair)
        if courses_to_replace and not self.replacer.is_alive():
            self.replacer.start()

    def can_select(self, course):
        return not any(are_overlap(c, course) for c in self.current)

    def __update_current(self):
        try:
            self.current = tuple(parse_current(self.main_sess.get(REMOVE_URL).text))
        except AttributeError:
            self.current = tuple(parse_current(self.sess.get(REMOVE_URL).text))


    def do_qcurrent(self, _):
        '''Print out current selected courses.'''
        self.__update_current()
        self.print_courses(self.current)

    @staticmethod
    def print_courses(courses):
        t = PrettyTable(['bsid', 'name', 'teacher', 'weekday', 'hour', 'week',
            'type'])
        # FIXME: This print method ignores even_week.
        for c in courses:
            course_time = c['odd_week'][0]
            weekday = course_time['weekday']
            hour = str(course_time['cbegin'])+'-'+str(course_time['cend'])
            week = str(course_time['wbegin'])+'-'+str(course_time['wend'])
            t.add_row([c.get('bsid', ''), c.get('name', ''), c.get('teacher',
                ''), weekday, hour, week, c.get('course_type', '')])
        print(t)

    def do_qnfull(self, _):
        ''' List all courses that are not full now.
        '''
        seen = set()
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            for i, state in enumerate(executor.map(self.is_full, self.courses)):
                if state:
                    course = self.courses[i]
                    if course['name'] in seen:
                        continue
                    seen.add(course['name'])
                    real_cid=parse_qs(urlparse(course['url']).query)['kcdm'][0]
                    hour = course['odd_week'][0]
                    # self.print_courses(course)
                    print(course['name']+'\t'+hour['weekday'],
                        hour['cbegin']+'-'+hour['cend'])

    def is_full(self, course):
        # fail_message='%e8%af%a5%e8%af%be%e8%af%a5%e6%97%b6%e9%97%b4%e6%ae%b5%e4%ba%ba%e6%95%b0%e5%b7%b2%e6%bb%a1%ef%bc%81'
        resp = self.sess.post(url=course['url'], data=course['param'],
            allow_redirects=False)
        if 'messagePage.aspx' in resp.text:
            return False
        else:
            return True

    def do_submit(self, _):
        try:
            print(self.main_sess.head(SUBMIT_URL).headers)
        except AttributeError:
            self.refresh_main_sess()
            print(self.main_sess.head(SUBMIT_URL).headers['Location'])

    def do_refresh(self, _):
        self.refresh_main_sess()

    def do_is_grabbing(self, _):
        print(not self.grabber.canceled)

    def do_is_replacing(self, _):
        print(not self.replacer.canceled)


if __name__ == '__main__':
    m1 = Main()
    quit = False

    while not quit:
        try:
            m1.cmdloop()
            quit = True
        except KeyboardInterrupt:
            try:
                print('Quiting gracefully. Interrupt twice to force quit.')
                m1.do_bye('')
                quit = True
            except KeyboardInterrupt:
                sys.exit(-1)
            sys.exit(0)
        except Exception as e:
            print(e)
            print('It seems something unexpected happened. ᕙ(⇀‸↼‶)ᕗ')
