#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import os
import sys
import logging

ASP_FORM_ID = ['__VIEWSTATE', '__VIEWSTATEGENERATOR', '__EVENTVALIDATION',
               '__EVENTTARGET', '__EVENTARGUMENT', '__LASTFOCUS']


EDU_URL = 'http://electsys.sjtu.edu.cn/edu/'
ELECT_URL = EDU_URL+'student/elect/'
MAIN_URL=ELECT_URL+'electcheck.aspx?xklc=2'
REMOVE_URL=ELECT_URL+'removeLessonFast.aspx'
SUBMIT_URL=ELECT_URL+'electSubmit.aspx'

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

def success(resp):
    if 'message' in resp.url:
        logger.warn(urlparse(resp.url)['message'])
        return False
    return True


def qiangke(sess, course):
    query = {'kcdm': course.cid,
            'xklx': '通识',
            'redirectForm': 'speltyCommonCourse.aspx',
            'yxdm': None,
            'tskmk': 420,
            'kcmk': -1,
            'nj': '无'
            }
    params = {'myradiogroup': course.bsid,
            '__EVENTTARGET': 'gridGModule$ctl' + course.xyid + '$radioButton',
            'LessonTime1$btnChoose': '选定此教师'
            }
    url = LESSON_URL+'viewLessonArrange.aspx?'+urlencode(query)
    return asp_post(sess, url=url, recover_url=url, params=params)

def asp_post(sess, url, recover_url, params, is_ok=success):
    # Save __EVENTTARGET in case it is overrided
    et = {'__EVENTTARGET': params.get('__EVENTTARGET')}
    # set_trace()
    asp = asp_params(sess.get(recover_url).text)
    params.update(asp)
    params.update(et)
    for cnt in count():
        try:
            resp = sess.post(url, data=params)
            resp.raise_for_status()
            set_trace()
            if is_ok(resp):
                return resp
            logger.info('Posting' + ' failed the ' + str(cnt) + ' times.')
        except requests.exceptions.HTTPError:
            logger.error('ASP params are wrong. Trying another time...')
            asp = asp_params(sess.get(recover_url).text)
            params.update(asp)
            params.update(et)


def asp_params(page):
    soup = BeautifulSoup(page, 'html.parser')
    return {inp['id']: inp['value'] for inp in soup.find_all('input') 
            if inp.has_attr('id') and inp['id'] in ASP_FORM_ID}

def main_page(sess, query='?xklc=1'):
    '''
    This function is useless.
    '''
    # query = '?xklc=1': 海选
    # query = '?xklc=2': 抢选
    # query = '?xklc=3': 第三轮选
    # return sess.get(ELECT_URL+'sltFromRcommandTbl.aspx')
    return asp_post(sess,
                    url=ELECT_URL + 'electwarning.aspx' + query,
                    recover_url=ELECT_URL + 'electwarning.aspx' + query,
                    params={'CheckBox1': 'on', 'btnContinue': '继续'},
                    # is_ok=lambda resp: '%e5%af%b9%e4%b8%8d%e8%b5%b7%2c' not in resp.url
                    )

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
