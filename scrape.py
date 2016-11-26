#! /usr/bin/env python3
# -*- encoding: utf-8 -*-

from jaccount import login
from sdtMain import asp_params
from pdb import set_trace
from logging import getLogger
from bs4 import BeautifulSoup
from lxml import etree
from io import StringIO
import requests

EDU_URL = 'http://electsys.sjtu.edu.cn/edu/'
LXML_RE_DICT = {'re': 'http://exslt.org/regular-expressions'}
TEST_RENWEN_HTML = 'http://localhost/ele/website/通识课-人文_files/speltyCommonCourse.html'

# TODO: Make a pool of cookies and asp_values
#       'some string' -> u'some string'??
class AspSession(object):
    logger = getLogger()
    urls = {'tongshi': EDU_URL+'elect/speltyCommonCourse.aspx',
            'renxuan': EDU_URL+'elect/outSpeltyEP.aspx',
            'kecheng': EDU_URL+'lesson/viewLessonArrange.aspx/'
            }
    # '__EVENTTARGET' should not get updated.
    ASP_FORM_ID = ['__VIEWSTATE', '__VIEWSTATEGENERATOR', '__EVENTVALIDATION',
                '__EVENTARGUMENT', '__LASTFOCUS']
    def __init__(self, username, password):
        self._sess = login(username, password)
        self.cookies = self._get_cookie()
        self.params = self._get_params()

    # TODO: Update a specific page's asp_param
    def update_params(self):
        logger.info('updating asp params...')
        self.params = self._get_params(_sess)

    def _get_cookie(self):
        ele_cookies_list = ['ASP.NET_SessionId', 'mail_test_cookie']
        return {s: _sess.cookies[s] for s in ele_cookies_list}

    def _get_params(self):
        param_dict = {}
        for page_name, url in urls.items():
            soup = BeautifulSoup(requests.get(url, cookies = self.cookies).text,
                    'html.parser')
            param_dict[page_name] = {inp['name']: inp['value']
                    for inp in soup.find_all('input')
                    if inp['name'] in ASP_FORM_ID
                    }
        return param_dict
    def post(url, params, *args, **kwargs):
        while True:
            try:
                resp = _sess.post(url = url, params = self.params, *args, **kwargs)
                resp.raise_for_status()
                return _sess.post(url = url, params = self.params, *args, **kwargs)
            except requests.exceptions.HTTPError:
                self.params.update(params)
                logger.info('params updated')

def tongshi_1(sess, leixing):
    page_name = 'tongshi'
    TONGSHI_ID = {'renwen': '02', 'sheke': '03', 'ziran': '04', 'shuxue': '05'}
    xyid = TONGSHI_ID[lexing]
    et_str = 'gridGModule$ctl'+xyid+'$radioButton'
    params = {et_str: 'radioButton', '__EVENTTARGET': et_str}

    resp = sess.post(url = urls[page_name], params = params)
    # TODO: Verify this success condition
    while '请勿' in resp.url:
        resp = sess.post(url = urls[page_name], params = params)
    return resp

def tongshi_2(sess, resp):
    parser = etree.HTMLParser()
    tree = etree.parse(StringIO(resp.text), parser)
    tr = tree.xpath('//table[@id="gridMain"]/tbody/tr[re:test(@class, "tdcolour\d$")]', namespaces = LXML_RE_DICT)
    if not tr: raise RuntimeError("Fetch tongshi_2 failed")
    cnames = [s.strip() for e in tr for s in e.xpath('./td[2]/text()') ]
    cids = [s.strip() for e in tr for s in e.xpath('./td[3]/text()') ]
    ccredits = [s.strip() for e in tr for s in e.xpath('./td[5]/text()') ]
    set_trace()
    for cid in cids:
        yield sess.post(url = urls[page_name],
                params = {'myradiogroup': str(cid), 'lessonArrange': '课程安排'}
        )

def lesson_arrange(resp):
    


if __name__ == '__main__':
    sess = requests.Session()
    tongshi_2(sess, sess.get(TEST_RENWEN_HTML))
    
# class TongShiSpider(Spider):
#     # name = 'tongshi'
#     # def prepare_param(self, response, xyid = None):
#     #     # ASP_PARA_LIST = ['__VIEWSTATE', '__VIEWSTATEGENERATOR',
#     #     # '__EVENTVALIDATION']
#     #     param_path = response.xpath('//input[re:test(@name, "__[A-Z]+")]')
#     #     params = {n:v for n in param_path.xpath('./@name') 
#     #             for v in param_path.xpath('./@value')}
#     #     params['gridGModule$ctl' + xyid + '$radioButton'] = 'radioButton' # ???
#     #     params['__EVENTTARGET'] = 'gridGModule$ctl' + xyid + '$radioButton'

#     def parse(self, response):
#         # set_trace()
#         # from scrapy.shell import inspect_response
#         # inspect_response(response, self)
#         return [FormRequest.from_response(response, 
#             formdata = {'CheckBox1': 'on', 'btnContinue' : '继续'},
#             callback = self.after_post
#         )]

#     def after_post(self, response):
#         if '%e5%af%b9%e4%b8%8d%e8%b5%b7%2c' in response.url:
#             return
#             [Request('file:///home/yuq/Documents/sjtu/electsys/website/通识课_files/speltyCommonCourse.html',
#                 callback=self.parse_tongshi)]

#     def parse_tongshi(self, response):
#         courses = response.xpath('//table[@id="gridMain"]/tbody/tr[re:test(@class, "tdcolour\d$")]')
#         from scrapy.shell import inspect_response
#         inspect_response(response, self)

#     def start_requests(self):
#         requests = Request('http://electsys.sjtu.edu.cn/edu/student/elect/electwarning.aspx',
#             cookies = login('zxdewr', 'sszh2sc'), 
#             dont_filter=True, 
#             callback=self.parse
#         )
#         renwen_request = FormRequest.from_response(

#         if type(requests) is list:
#             for request in requests:
#                 yield request
#         else:
#             yield requests



