#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import os
import sys
import logging
import re
ASP_FORM_ID = ['__VIEWSTATE', '__VIEWSTATEGENERATOR', '__EVENTVALIDATION',
               '__EVENTTARGET', '__EVENTARGUMENT', '__LASTFOCUS']


EDU_URL = 'http://electsys.sjtu.edu.cn/edu/'
LESSON_URL = EDU_URL+'lesson/viewLessonArrange.aspx'
ELECT_URL = EDU_URL+'student/elect/'
MAIN_URL = ELECT_URL+'electcheck.aspx?xklc=2'
REMOVE_URL = ELECT_URL+'removeLessonFast.aspx'
SUBMIT_URL = ELECT_URL+'electSubmit.aspx'
MAIN_URL = ELECT_URL+'electcheck.aspx?xklc=2'
RECOMMAND_URL = ELECT_URL+'RecommandTblOuter.aspx'


# FIXME: Multiple call not checked, is that ok?
def get_logger(module_name):
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARN)
    ch.setFormatter(formatter)

    LOG_PATHNAME = os.path.dirname(os.path.abspath(__file__))+'/log'
    try:
        os.mkdir(LOG_PATHNAME)
    except FileExistsError:
        pass
    try:
        LOG_FILENAME = sys.argv[1]+'-qiangke'
    except IndexError:
        LOG_FILENAME = 'qiangke'

    fh = logging.FileHandler('{}/{}.log'.format(LOG_PATHNAME, LOG_FILENAME))
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger

logger = get_logger(__name__)

def asp_params(page):
    soup = BeautifulSoup(page, 'html.parser')
    return {inp['id']: inp['value'] for inp in soup.find_all('input')
            if inp.has_attr('id') and inp['id'] in ASP_FORM_ID}

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

class SessionOutdated(Exception):
    pass

class CourseFull(Exception):
    pass

class EmptyCourse(Exception):
    pass

class FrequencyError(Exception):
    pass

class MessageError(Exception):
    pass
