#! /usr/bin/env python
# -*- coding: utf-8 -*-

from scrapy import Spider, FormRequest, Request, Item, Field
from scrapy.loader import ItemLoader
from scrapy.shell import inspect_response
from jaccount import login
# from sdtMain import asp_params
from pdb import set_trace
from logging import getLogger
from bs4 import BeautifulSoup
from functools import wraps
from course_collector.items import Course, CourseTime
import queue
import requests
import re

EDU_URL = 'http://electsys.sjtu.edu.cn/edu/'
ELECT_URL = EDU_URL+'student/elect/'
LESSON_URL = 'http://electsys.sjtu.edu.cn/edu/lesson/'
TEST_LESSON_URL = 'http://localhost/ele/website/%E9%80%9A%E8%AF%86%E8%AF%BE-%E4%BA%BA%E6%96%87-%E7%A7%AF%E6%9E%81%E5%BF%83%E7%90%86%E5%AD%A6_files/viewLessonArrange.html'
# TEST_LESSON_URL = 'http://localhost/ele/website/%E4%BD%93%E8%82%B2%283%29_files/viewLessonArrange.html'
TEST_TONGSHI_URL = 'http://localhost/ele/website/%E9%80%9A%E8%AF%86%E8%AF%BE_files/speltyCommonCourse.html'
TEST_RENWEN_URL = 'http://localhost/ele/website/%E9%80%9A%E8%AF%86%E8%AF%BE-%E4%BA%BA%E6%96%87_files/speltyCommonCourse.html'
TEST_RENXUAN_URL = 'http://localhost/ele/website/%E4%BB%BB%E9%80%89%E8%AF%BE-%E8%88%B9%E5%BB%BA_files/outSpeltyEP.html'
TEST_SHUXUE_URL = 'http://localhost/ele/website/%E4%BB%BB%E9%80%89%E8%AF%BE-%E6%95%B0%E5%AD%A6_files/outSpeltyEP.html'
TEST_FULL_URL = 'http://localhost/ele/website/%28%E9%80%89%E7%A7%AF%E6%9E%81%E5%BF%83%E7%90%86%E5%AD%A6%29%E4%BA%BA%E6%BB%A1%E4%BA%86_files/messagePage.html'

logger = getLogger(__name__)

# TODO: Make a pool of cookies and asp_values
# TODO: Add Exception handling: if '对不起' in resp.url: yield response.request
# TODO: Add Feed Expoter
# TODO: debug from_response method 
# TODO: Add exception handler: Frequency limited
# class AspSession(object):
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

# class ItemLoader(ItemLoader):
    # default_input_processor = MapCompose(lambda v: v.strip(), replace_escape_chars)
    # default_input_processor = MapCompose(str.strip)

class TongShiSpider(Spider):
    name = 'tongshi'
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

    # def test_wrapper(self):
    #     def decorator(self, func):
    #         @wraps(func)
    #         def wrapper(*args, **kwargs):
    #             for request in func(*args, **kwargs):
    #                 yield request
    #         return wrapper
    #     return decorator

    def tongshi_1(self, response):
        for course_type in ['02', '03', '04', '05']:
            et_str = 'gridGModule$ctl'+course_type+'$radioButton'
            params = {et_str: 'radioButton', '__EVENTTARGET': et_str}
            item = Course()
            item['course_type'] = course_type
            yield Request(url=TEST_RENWEN_URL, 
                    dont_filter=True,
                    meta= {'item':item},
                    callback = self.tongshi_2
            )
            # yield FormRequest.from_response(
            #         response, 
            #         url = TEST_RENWEN_URL,# ELECT_URL+'speltyCommonCourse.aspx'
            #         formdata = params,
            #         meta = {'item': item}, 
            #         callback = self.tongshi_2
            # )

    def tongshi_2(self, response):
        trs = response.xpath('//table[@id="gridMain"]/tbody/tr[re:test(@class,"tdcolour\d$")]')
        assert trs
        for tr in trs:
            loader = ItemLoader(response.meta['item'], selector=tr)
            cid = loader.get_xpath('./td[3]/text()')
            loader.add_xpath('name', './td[2]/text()')
            loader.add_xpath('cid', './td[3]/text()')
            loader.add_xpath('credit', './td[5]/text()')
            yield Request(url=TEST_LESSON_URL, 
                    dont_filter=True,
                    meta= {'item':loader.load_item()},
                    callback = self.lesson_parser
            )
            # yield FormRequest.from_response(
            #     response, 
            #     url = TEST_LESSON_URL,# ELECT_URL+'viewLessonArrange.aspx'
            #     formdata={'myradiogroup': str(cid),'lessonArrange': '课程安排'},
            #     meta={'item': loader.load_item()},
            #     callback=self.lesson_parser
            # )
        # cnames = [s.strip() for s in tr.xpath('./td[2]/text()').extract()]
        # cids = [s.strip() for s in tr.xpath('./td[3]/text()').extract()]
        # ccredits = [s.strip() for s in tr.xpath('./td[5]/text()').extract()]
        # assert len(cnames) == len(cids)
        # assert len(cnames) == len(ccredits)
        # set_trace()
        # for name, cid, credit in zip(cnames, cids, ccredits):
        #     loader = ItemLoader(response.meta['item'], response=response)
        #     loader.add_value('name', name)
        #     loader.add_value('cid', cid)
        #     loader.add_value('credit', credit)

    def lesson_parser(self, response):
        # FIXME: Replace these functions with nested item loaders.
        # https://doc.scrapy.org/en/latest/topics/loaders.html#nested-loaders
        def __weekday_parse(info_lst):
            def __do_parse(info_str):
                def __to_item(infos):
                    items = []
                    for info in infos:
                        item = CourseTime()
                        item['weekday'] = info[0]
                        item['cbegin'] = info[1]
                        item['cend'] = info[2]
                        item['wbegin'] = info[3]
                        item['wend'] = info[4]
                        items.append(item)
                    return items
                weeks=__to_item(re.findall(r'星期(\w)\s*第(\d+)节--第(\d+)节\s*(?:.*)\((\d+)-(\d+)周\)\.',info_str))
                # FIXME: This regex fails when weeks of 2 teachers teach differ.
                places=re.findall(r'星期(?:\w)\s*第(?:\d+)节--第(?:\d+)节\s*(.*)\((?:\d+)-(?:\d+)周\)\.',info_str)
                # weeks = set(re.findall(r'\((\d+)-(\d+)周\)\.', info_str))
                # set_trace()
                # weekday = re.findall(r'星期(\w)', info_str)
                # hour = re.findall(r'第(\d+)节--第(\d+)节', info_str)
                # for ws, wd, h in zip(weeks, weekday, hour):
                #     set_trace()
                #     week_time.append(' '.join(ws)+'日一二三四五六'.index(wd)+' '.join(h))
                #     logger.debug(week_time)
                # odd_week = str('日一二三四五六'.index(odd['weekday']))+' '+
                #         str(odd['hour'][0])+' '+str(odd['hour'][1])
                return {'time': weeks, 'place': places}
                        # 'teacher': re.findall(r'\.(\w+)\s(\w+)',info_str)# 教师 职称}
            try:
                odd = info_lst[info_lst.index('单周')+1:info_lst.index('双周')]
                even = info_lst[info_lst.index('双周')+1:]
                odd, even = [__do_parse(''.join(lines)) for lines in [odd, even]]
            except ValueError:
                odd = __do_parse(''.join(info_lst))
                even = __do_parse(''.join(info_lst))

            if odd['place'] == even['place']:
                place = odd['place']
            else:
                place = 'odd: '+' '.join(odd['place'])+' even: '+' '.join(even['place'])
            return odd['time'], even['time'], place
            # return (' '.join(str(i) for i in odd['time']),
            #         ' '.join(str(i) for i in even['time']),
            #         place)

        trs = response.xpath('//table[@id="LessonTime1_gridMain"]/tbody/tr[re:test(@class,"tdcolour\d$")]')
        assert trs
        # inspect_response(response, self)
        for tr in trs:
            odd_week, even_week, place = __weekday_parse(tr.xpath('./td[10]/text()').extract())
            loader = ItemLoader(response.meta['item'], selector=tr)
            loader.add_xpath('bsid', './/input[@name="myradiogroup"]/@value')
            loader.add_xpath('teacher', './td[2]/text()')
            # loader.add_xpath('duration', './td[5]/text()')
            loader.add_xpath('max_member', './td[6]/text()')
            loader.add_xpath('min_member', './td[7]/text()')
            loader.add_xpath('remark', './td[11]/text()')
            loader.add_value('place', place)
            # loader.add_xpath('week', ' ./td[10]/text()')
            loader.add_value('odd_week', odd_week)
            loader.add_value('even_week', even_week)
            # week_chunk = trs.xpath('./td[10]/text()')
            yield loader.load_item()


#         def parse(text):
#             try:
#                 schooltime = text.split('星期')[1]
#                 weekday = '日一二三四五六'.index(schooltime[0])
#                 period = tuple(int(i) for i in re.findall(r'\d+',schooltime))
#                 assert len(period) == 2
#                 return {weekday: period}
#             except IndexError:
#                 return {}

#         parsed = {'单周':{}, '双周':{}}
#         if '单周' in info_lst:
#             single_week = True
#             for text in info_lst:
#                 if text == '双周': single_week = False
#                 parsed['单周' if single_week else '双周'].update(parse(text))
#         else:
#             for text in info_lst:
#                 parsed['单周'].update(parse(text))
#                 parsed['双周'].update(parse(text))
#         return str(parsed)


    def renxuan_1(self, response):
        facaulties = response.xpath('//select[@name="OutSpeltyEP1$dpYx"]/option')
        for facaulty in facaulties:
            for grade in ['2014', '2015', '2016']:
                params = {'OutSpeltyEP1$dpYx': facaulty.extract(),
                        'OutSpeltyEP1$dpNj': grade,
                        'OutSpeltyEP1$btnQuery': '查 询'
                        }
                loader = ItemLoader(Course(), selector=facaulty)
                loader.add_xpath('course_type', './@value')
                yield Request(url=TEST_SHUXUE_URL, 
                        dont_filter=True, 
                        meta= {'item':loader.load_item()},
                        callback = self.renxuan_2
                )
                # yield FormRequest.from_response(
                #         response, 
                #         formdata = params,
                #         meta = {'item': loader.load_item()}, 
                #         callback = self.renxuan_2
                # )

    def renxuan_2(self, response):
        trs = response.xpath('//table[@id="OutSpeltyEP1_gridMain"]/tbody/tr[re:test(@class,"tdcolour\d$")]')
        for tr in trs:
            loader = ItemLoader(response.meta['item'], selector=tr)
            cid = loader.get_xpath('./td[3]/text()')
            loader.add_xpath('name', './td[2]/text()')
            loader.add_xpath('cid', './td[3]/text()')
            loader.add_xpath('credit', './td[6]/text()')
            yield Request(url=TEST_LESSON_URL, 
                    dont_filter=True, 
                    meta= {'item':loader.load_item()},
                    callback = self.lesson_parser
            )
            # yield FormRequest.from_response(
            #         response,
            #         formdata={
            #             'OutSpeltyEP1$dpYx':response.meta['item']['course_type'],
            #             'OutSpeltyEP1$dpNj':response.meta['item']['grade'],
            #             'myradiogroup':cid,
            #             'OutSpeltyEP1$lessonArrange': '课程安排'
            #         },
            #         meta={'item': loader.load_item()},
            #         callback=self.lesson_parser
            # )

    def qiangke(self, course):
        if course.course_type in ['02', '03', '04', '05']:
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
        else:
            query = {'kcdm': course.cid,
                    'xklx': '选修',
                    'redirectForm': 'outSpeltyEp.aspx',
                    'yxdm': course.course_type,
                    # FIXME: nj may vary
                    'nj': 2015,
                    'kcmk':-1,
                    'txkmk': -1
                    }
            params = {'myradiogroup': course.bsid,
                    'LessonTime1$btnChoose': '选定此教师'
                    }
        url = LESSON_URL+'viewLessonArrange.aspx?'+urlencode(query)
        yield Request(url=url, dont_filter=True, callback=self.qiangke,
                meta={'params': params, 'course_name': course.name})

    def __do_qiangke(self, response):
        yield FormRequest.from_response(response,
                 # url= ELECT_URL+'electwarning.aspx?xklc=1',# TEST_FULL_URL,
                 formdata=response.meta['params'],
                 dont_filter=True,
                 callback=self.submit
                 )

    def submit(self, response):
        yield FormRequest.from_response(response,
                formdata={'btnSubmit', '选课提交'},
                dont_filter=True)
        logger.critical('Course %s got!'%response.meta['course_name'])


    def start_requests(self):
         yield Request(TEST_TONGSHI_URL,# ELECT_URL+'speltyCommonCourse.aspx',
            dont_filter=True, 
            callback=self.tongshi_1
        )
         # yield Request(TEST_RENXUAN_URL,# ELECT_URL+'outSpeltyEP.aspx',
         #    dont_filter=True, 
         #    callback=self.renxuan_1
        # )
         # yield Request(ELECT_URL+'electwarning.aspx?xklc=1',
         #         dont_filter=True,
         #         callback=self.test)

    def test(self, response):
        # inspect_response(response, self)
        r = FormRequest.from_response(response,
                 url= ELECT_URL+'electwarning.aspx?xklc=1',# TEST_FULL_URL,
                 formdata={'CheckBox1': 'on', 'btnContinue': '继续'},
                 dont_filter=True,
                 callback=self.test)
        # print(r)
        # set_trace()
        yield r

    def __init__(self, username, password):
        self.user = username
        self.passwd = password
        # self.cqueue = [queue.Queue()]

    # def after_post(self, response):
    #     if '%e5%af%b9%e4%b8%8d%e8%b5%b7%2c' in response.url:
    #         return
    #         [Request('file:///home/yuq/Documents/sjtu/electsys/website/通识课_files/speltyCommonCourse.html',
    #             callback=self.parse_tongshi)]

    # def parse_tongshi(self, response):
    #     courses = response.xpath('//table[@id="gridMain"]/tbody/tr[re:test(@class, "tdcolour\d$")]')
    #     from scrapy.shell import inspect_response
    #     inspect_response(response, self)


    #     # if type(requests) is list:
    #     #     for request in requests:
    #     #         yield request
    #     # else:
    #     #     yield requests

