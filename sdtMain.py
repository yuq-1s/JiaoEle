#! /usr/bin/env python3
from jaccount import login
from pdb import set_trace
from bs4 import BeautifulSoup
import requests
from logging import getLogger, StreamHandler, Formatter, DEBUG
from itertools import count
from functools import wraps
from sys import stdout
from urllib.parse import urlencode, urlparse

# TODO:
#   1. Try to grab courses directly.(not step by step from main page)

# When in main page (aka path /)
ELECT_URL = 'http://electsys.sjtu.edu.cn/edu/student/elect/'
LESSON_URL = 'http://electsys.sjtu.edu.cn/edu/lesson/'
# MAIN_PAGE_URL = ELECT_URL+'sltFromRcommandTbl.aspx'


ASP_FORM_ID = ['__VIEWSTATE', '__VIEWSTATEGENERATOR', '__EVENTVALIDATION',
               '__EVENTTARGET', '__EVENTARGUMENT', '__LASTFOCUS']
# logger = getLogger(__name__)

# ch = StreamHandler(stdout)
# ch.setLevel(DEBUG)
# formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# ch.setFormatter(formatter)
# logger.addHandler(ch)


def success(resp):
    if 'message' in resp.url:
        logger.warn(urlparse(resp.url)['message'])
        return False
    return True

def asp_post(sess, url, recover_url, params, is_ok=success):
    # Save __EVENTTARGET in case it is overrided
    et = {'__EVENTTARGET': params.get('__EVENTTARGET')}
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
    return {inp['name']: inp['value'] for inp in soup.find_all('input') if
            inp['name'] in ASP_FORM_ID}


def main_page(sess, query='?xklc=1'):
    '''
    This function is useless.
    '''
    # query = '?xklc=1': 海选
    # query = '?xklc=2': 抢选
    # query = '?xklc=3': 第三轮选
    return sess.get(ELECT_URL+'sltFromRcommandTbl.aspx')
    # return asp_post(sess,
    #                 url=ELECT_URL + 'electwarning.aspx' + query,
    #                 recover_url=ELECT_URL + 'electwarning.aspx',
    #                 params={'CheckBox1': 'on', 'btnContinue': '继续'},
    #                 # is_ok=lambda resp: '%e5%af%b9%e4%b8%8d%e8%b5%b7%2c' not in resp.url
    #                 )

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


class course(object):
    def __init__(self, **kwargs):
        self.cid = kwargs['cid']
        self.bsid = kwargs['bsid']
        self.xyid = kwargs['xyid']

if __name__ == '__main__':
    test_course = course(**{'cid': 'PS900', 'bsid': '456723', 'xyid': 'ba231'})
    # qiangke(requests.Session(), test_course)
    main_page(login('zxdewr', 'pypy11u'))
    # sess = login('zxdewr', 'p1ptess')
    # init(sess)


# def autition(sess):
#     # Get this site also work ???
#     # http://electsys.sjtu.edu.cn/edu/student/elect/electcheck.aspx?xklc=1
#     # resp = sess.post(xkurl, data = prepare_form('?xklc=1'))
#     # Can I do not assign sess?
#     # sess, form = init(sess, query='?xklc=1')
#     return init(sess, query='?xklc=1')

# def prepare_cookie(sess):
#     ele_cookies_list = ['ASP.NET_SessionId', 'mail_test_cookie']
#     return {s: sess.cookies[s] for s in ele_cookies_list}

# def check_form(recover_url):
#     logger = logging.getLogger(__name__)
#     asp = asp_form(sess.get(recover_url).text)
#     form.update(asp)
#     def decorator(f):
#         @wraps(f)
#         def wrapper(sess, form):
#             try:
#                 return f(sess, form)
#             except requests.exceptions.HTTPError:
#                 logger.warn('ASP params are wrong. Trying another time...')
#                 asp = asp_form(sess.get(recover_url).text)
#                 return f(sess, form.update(asp))
#             raise RuntimeError('Fetching ASP params failed')
#         return wrapper
#     return decorator


# def until(is_okay):
#     def decorator(f):
#         @wraps(f)
#         def wrapper(*args):
#             result = f(*args)
#             for cnt in count():
#                 logger.debug(f.__name__ + ' failed the ' + cnt ' times.')
#                 if is_okay(result):
#                     break
#                 result = f(*args)
#             return result
#         return wrapper
#     return decorator


# @until(lambda url: '%e5%af%b9%e4%b8%8d%e8%b5%b7%2c' not in url)
# @check_form(ELECT_URL+'speltyCommonCourse.aspx', {'btnSubmit', '选课提交'})
# def do_submit(sess, form):
#     resp = sess.post(ELECT_URL+'electwarning.aspx', data=form)
#     resp.raise_for_status()
#     return resp.url

# def init(sess, query):
#     # The same as clicking '海选' in the main page
#     # Speed: about 25 posts per second when the server is not busy
#     # TODO:
#     #   1. Throw exception when __EVENTVALIDATION is out of date
#     #   2. Get /edu/student/elect/electcheck.aspx?xklc=1 directly may work
#     #       resp = sess.get(TARGET_URL+'student/elect/electcheck.aspx'+query)
#     #   3. Abort redirection when next url '对不起' to promote speed
#     #       resp = sess.post(xkurl, data = form, allow_redirects = False)
#     #       while resp.status_code != 200 and '%e5%af%b9%e4%b8%8d%e8%b5%b7%2c' not in resp.url:
#     #           print(resp.url)
#     #           resp = sess.get(resp.url, allow_redirects = False)
#     '对不起,你目前不能进行该轮选课'
#     '''%e5%af%b9%e4%b8%8d%e8%b5%b7%2c%e4%bd%a0%e7%9b%ae%e5%89%8d%e4%b8%8d\
#         %e8%83%bd%e8%bf%9b%e8%a1%8c%e8%af%a5%e8%bd%ae%e9%80%89%e8%af%be'''
#     xkurl = ELECT_URL + 'electwarning.aspx'
#     form = prepare_form(sess, query)
#     while True:
#         try:
#             # if any item of asp.net form missing we will get electwarning.aspx
#             assert len(form) >= 5
#             resp = sess.post(xkurl, data=form)
#             resp.raise_for_status()
#             if '%e5%af%b9%e4%b8%8d%e8%b5%b7%2c' not in resp.url:
#                 return sess, asp_form(resp.text)
#             else:
#                 print('Trying to crowd into main')
#         except requests.exceptions.HTTPError:
#             print('Updating form...')
#             form = prepare_form(sess, query)

#     ''' For debugging purpose'''
#     # for i in count():
#     #     resp = sess.post(xkurl, data = form)
#     #     if '%e5%af%b9%e4%b8%8d%e8%b5%b7%2c' not in resp.url:
#     #         return sess

#     #     if not i%100:
#     #         print('Trying to login for ' + str(i) + ' times')
#     #     if not i % 500 and i != 0:
#     #         set_trace()


# # update ASP.NET validation
