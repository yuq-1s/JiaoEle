#! /usr/bin/env python
# -*- coding: utf-8 -*-

from scrapy import Spider, FormRequest, Request, Item, Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose
from scrapy.shell import inspect_response
from jaccount import login
# from sdtMain import asp_params
from pdb import set_trace
from logging import getLogger
from bs4 import BeautifulSoup
import requests

EDU_URL = 'http://electsys.sjtu.edu.cn/edu/'
ELECT_URL = EDU_URL+'student/elect/'
TEST_LESSON_URL = 'http://localhost/ele/website/%E4%BD%93%E8%82%B2%283%29_files/viewLessonArrange.html'
TEST_TONGSHI_URL = 'http://localhost/ele/website/%E9%80%9A%E8%AF%86%E8%AF%BE_files/speltyCommonCourse.html'
TEST_RENWEN_URL = 'http://localhost/ele/website/%E9%80%9A%E8%AF%86%E8%AF%BE-%E4%BA%BA%E6%96%87_files/speltyCommonCourse.html'

# TODO: Make a pool of cookies and asp_values
# class AspSession(object):
#     logger = getLogger()
#     urls = {'tongshi': EDU_URL+'elect/speltyCommonCourse.aspx',
#             'renxuan': EDU_URL+'elect/outSpeltyEP.aspx',
#             'kecheng': EDU_URL+'lesson/viewLessonArrange.aspx/'
#             }
#     ASP_FORM_ID = ['__VIEWSTATE', '__VIEWSTATEGENERATOR', '__EVENTVALIDATION',
#             '__EVENTARGUMENT', '__LASTFOCUS']
#     def __init__(self, username, password):
#         self._sess = login(username, password)
#         self.cookies = self._get_cookie()
#         self.params = self._get_params()

#     # TODO: Update a specific page's asp_param
#     def update_params(self):
#         logger.info('updating asp params...')
#         self.params = self._get_params(_sess)

#     def _get_cookie(self):
#         ele_cookies_list = ['ASP.NET_SessionId', 'mail_test_cookie']
#         return {s: _sess.cookies[s] for s in ele_cookies_list}

#     def _get_params(self):
#         param_dict = {}
#         for page_name, url in urls.items():
#             soup = BeautifulSoup(requests.get(url, cookies = self.cookies).text,
#                     'html.parser')
#             param_dict[page_name] = {inp['name']: inp['value']
#                     for inp in soup.find_all('input')
#                     if inp['name'] in ASP_FORM_ID
#                     }
#         return param_dict
#     def post(url, params, *args, **kwargs):
#         self.params.update(params)
#         return _sess.post(url = url, params = self.params, *args, **kwargs)

# def tongshi(sess)
#     TONGSHI_PARAMS = 
#     sess.post(url = urls['tongshi'], 

class Course(Item):
    course_type = Field()
    cid = Field()
    name = Field()
    credit = Field()
    teacher = Field()
    duration = Field()
    week = Field()
    bsid = Field()
    remark = Field()

class CourseItemLoader(ItemLoader):
    # default_input_processor = MapCompose(lambda v: v.strip(), replace_escape_chars)
    default_input_processor = MapCompose(str.strip)

class TongShiSpider(Spider):
    # name = 'tongshi'
    # def prepare_param(self, response, xyid = None):
    #     # ASP_PARA_LIST = ['__VIEWSTATE', '__VIEWSTATEGENERATOR',
    #     # '__EVENTVALIDATION']
    #     param_path = response.xpath('//input[re:test(@name, "__[A-Z]+")]')
    #     params = {n:v for n in param_path.xpath('./@name') 
    #             for v in param_path.xpath('./@value')}
    #     params['gridGModule$ctl' + xyid + '$radioButton'] = 'radioButton' # ???
    #     params['__EVENTTARGET'] = 'gridGModule$ctl' + xyid + '$radioButton'

    # def parse(self, response):
    #     # set_trace()
    #     # from scrapy.shell import inspect_response
    #     # inspect_response(response, self)
    #     return [FormRequest.from_response(response, 
    #         formdata = {'CheckBox1': 'on', 'btnContinue' : '继续'},
    #         callback = self.after_post
    #     )]

    def tongshi_1(self, response):
        for course_type in ['02', '03', '04', '05']:
            et_str = 'gridGModule$ctl'+course_type+'$radioButton'
            params = {et_str: 'radioButton', '__EVENTTARGET': et_str}
            item = Course()
            item.course_type = course_type
            yield FormRequest.from_response(
                    response, 
                    formdata = params,
                    meta = {'item': item}, 
                    callback = self.tongshi_2
            )

    def tongshi_2(self, response):
        trs = response.xpath('//table[@id="gridMain"]/tbody/tr[re:test(@class,"tdcolour\d$")]')
        assert trs
        for tr in trs:
            loader = CourseItemLoader(response.meta['item'], selector=tr)
            cid = loader.get_xpath('./td[3]/text()')
            loader.add_xpath('name', './td[2]/text()')
            loader.add_xpath('cid', './td[3]/text()')
            loader.add_xpath('credit', './td[5]/text()')
            yield FormRequest.from_response(
                response, 
                formdata={'myradiogroup': str(cid),'lessonArrange': '课程安排'},
                meta={'item': loader.load_item()},
                callback=self.lesson_parser
            )
        # cnames = [s.strip() for s in tr.xpath('./td[2]/text()').extract()]
        # cids = [s.strip() for s in tr.xpath('./td[3]/text()').extract()]
        # ccredits = [s.strip() for s in tr.xpath('./td[5]/text()').extract()]
        # assert len(cnames) == len(cids)
        # assert len(cnames) == len(ccredits)
        # set_trace()
        # for name, cid, credit in zip(cnames, cids, ccredits):
        #     loader = CourseItemLoader(response.meta['item'], response=response)
        #     loader.add_value('name', name)
        #     loader.add_value('cid', cid)
        #     loader.add_value('credit', credit)

    def lesson_parser(self, response):
        trs = response.xpath('//table[@id="LessonTime1_gridMain"]/tbody/tr[re:test(@class,"tdcolour\d$")]')
        assert trs
        for tr in trs:
            loader = CourseItemLoader(response.meta['item'], selector=tr)
            loader.add_xpath('bsid', './/input[@name="myradiogroup"]/@value')
            loader.add_xpath('teacher', './td[1]/text()')
            loader.add_xpath('duration', './td[4]/text()')
            loader.add_xpath('max_member', './td[5]/text()')
            loader.add_xpath('min_member', './td[6]/text()')
            loader.add_xpath('week', './td[9]/text()')
            loader.add_xpath('remark', './td[10]/text()')
            yield loader.load_item()

    def renxuan_1(self, response):
        facaulties = response.xpath('//select[@name="OutSpeltyEP1$dpYx"]/option/@value')
        for facaulty in facaulties:
            for grade in ['2014', '2015', '2016']:
                params = {'OutSpeltyEP1$dpYx': facaulty.extract(),
                        'OutSpeltyEP1$dpNj': grade,
                        'OutSpeltyEP1$btnQuery': '查 询'
                        }
                loader = CourseItemLoader(Course(), selector=facaulty)
                loader.add_xpath('course_type', '.')
                yield FormRequest.from_response(
                        response, 
                        formdata = params,
                        meta = {'item': loader.load_item()}, 
                        callback = self.renxuan_2
                )

    def renxuan_2(self, response):
        trs = response.xpath('//table[@id="OutSpeltyEP1_gridMain"]/tbody/tr[re:test(@class,"tdcolour\d$")]')
        for tr in trs:
            loader = CourseItemLoader(response.meta['item'], selector=tr)
            cid = loader.get_xpath('./td[3]/text()')
            loader.add_xpath('name', './td[2]/text()')
            loader.add_xpath('cid', './td[3]/text()')
            loader.add_xpath('credit', './td[6]/text()')
            yield FormRequest.from_response(
                    response,
                    formdata={
                        'OutSpeltyEP1$dpYx':response.meta['item']['course_type'],
                        'OutSpeltyEP1$dpNj':response.meta['item']['grade'],
                        'myradiogroup':cid,
                        'OutSpeltyEP1$lessonArrange': '课程安排'
                    },
                    meta={'item': loader.load_item()},
                    callback=self.lesson_parser
            )

    def start_requests(self):
         yield Request(TEST_TONGSHI_URL,# ELECT_URL+'speltyCommonCourse.aspx',
            cookies = self.cookies,
            dont_filter=True, 
            callback=self.tongshi_1
        )
         yield Request(TEST_RENXUAN_URL,# ELECT_URL+'outSpeltyEP.aspx',
            cookies = self.cookies,
            dont_filter=True, 
            callback=self.renxuan_1
        )

    def __init__(self, username, password):
        self.cookies = login('zxdewr', 'sszh2sc')

    def after_post(self, response):
        if '%e5%af%b9%e4%b8%8d%e8%b5%b7%2c' in response.url:
            return
            [Request('file:///home/yuq/Documents/sjtu/electsys/website/通识课_files/speltyCommonCourse.html',
                callback=self.parse_tongshi)]

    def parse_tongshi(self, response):
        courses = response.xpath('//table[@id="gridMain"]/tbody/tr[re:test(@class, "tdcolour\d$")]')
        from scrapy.shell import inspect_response
        inspect_response(response, self)


        # if type(requests) is list:
        #     for request in requests:
        #         yield request
        # else:
        #     yield requests

