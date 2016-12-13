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
from urllib.parse import urlencode
from time import sleep
import copy
import queue
import requests
import re
import os
import threading
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

class TongShiSpider(Spider):
    # json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
    # if value of 'ITEM_PIPELINES' is not dict
    name = 'tongshi'
    custom_settings = {
            'FEED_URI': 'file://'+os.getcwd()+'/data/courses.json',
            'DOWNLOAD_DELAY' : 0,
            'FEED_FORMAT': 'json',
            'FEED__EXPORT_ENCODING': 'utf-8',
            'MYCOOKIE_ENABLED': True,
            'ITEM_PIPELINES':{'course_collector.pipelines.collector.CourseCollectorPipeline':300},
            'DEFAULT_REQUEST_HEADERS':{'Referer':ELECT_URL+'speltyCommonCourse.aspx'}
            }

    def tongshi_stuck(self, response):
            yield FormRequest.from_response(
                response,
                dont_filter=True,
                url=ELECT_URL+'speltyCommonCourse.aspx',
                formdata={'gridGModule$ctl02$radioButton': 'radioButton'},
                callback=lambda _: None
                # callback=lambda response: inspect_response(response, self)
            )
            sleep(1)
            yield response.request

    def tongshi_1(self, response):
        for course_type in ['02', '03', '04', '05']:
            et_str = 'gridGModule$ctl'+course_type+'$radioButton'
            params = {et_str: 'radioButton', '__EVENTTARGET': et_str}
            item = Course()
            item['course_type'] = course_type
            # yield Request(url=TEST_RENWEN_URL, 
            #         dont_filter=True,
            #         meta= {'item':item},
            #         callback = self.tongshi_2
            # )
            yield FormRequest.from_response(
                    response, 
                    dont_filter=True,
                    url = ELECT_URL+'speltyCommonCourse.aspx',
                    formdata = params,
                    meta = {'item': item}, 
                    callback = self.tongshi_2
            )

    def tongshi_2(self, response):
        def __get_req(tr):
            item = copy.deepcopy(response.meta['item'])
            item['name'] = tr.xpath('./td[2]/text()').extract_first().strip()
            item['cid'] = tr.xpath('./td[3]/text()').extract_first().strip()
            item['credit'] = tr.xpath('./td[5]/text()').extract_first().strip()
            # query = {'kcdm': cid,
            #         'xklx': '通识',
            #         'redirectForm': 'speltyCommonCourse.aspx',
            #         'yxdm': '',
            #         'tskmk': 440,
            #         'kcmk': -1,
            #         'nj': '无'
            #         }
            # yield Request(url=TEST_LESSON_URL, 
            #         dont_filter=True,
            #         meta= {'item': copy.deepcopy(loader.load_item())},
            #         callback = self.lesson_parser
            # )

            # WHAT_THE_FUCK: All reqs are updated when a new one is yielded
            loader = ItemLoader(response.meta['item'], selector=tr)
            et_str = 'gridGModule$ctl'+response.meta['item']['course_type']+'$radioButton'
            loader.add_xpath('name', './td[2]/text()')
            loader.add_xpath('cid', './td[3]/text()')
            loader.add_xpath('credit', './td[5]/text()')
            new_meta = response.meta
            new_meta.update({'item': copy.deepcopy(loader.load_item())})
            yield FormRequest.from_response(
                response, 
                dont_filter=True,
                url=ELECT_URL+'speltyCommonCourse.aspx',
                formdata={et_str: 'radioButton',
                    'myradiogroup': str(item['cid']),'lessonArrange': '课程安排'},
                meta=new_meta, # {'item': item},
                callback=self.lesson_parser
            )
            # # sleep(0.9)
            # logger.debug(req.meta['item']['name'])
            # logger.debug(req.meta)
            # # set_trace()
            # return req

        trs = response.xpath('//table[@id="gridMain"]/tr[re:test(@class,"tdcolour\d$")]')
        # inspect_response(response, self)
        assert trs
        # a = __get_req(item, trs[0]).copy()
        # b = __get_req(item, trs[1]).copy()
        # logger.debug(a.meta)
        # logger.debug(b.meta)
        for tr in trs:
            loader = ItemLoader(response.meta['item'], selector=tr)
            et_str = 'gridGModule$ctl'+response.meta['item']['course_type']+'$radioButton'
            loader.add_xpath('name', './td[2]/text()')
            loader.add_xpath('cid', './td[3]/text()')
            loader.add_xpath('credit', './td[5]/text()')
            new_meta = response.meta
            new_meta.update({'item': copy.deepcopy(loader.load_item())})
            yield FormRequest.from_response(
                response, 
                dont_filter=True,
                url=ELECT_URL+'speltyCommonCourse.aspx',
                formdata={et_str: 'radioButton',
                    'myradiogroup': str(new_meta['item']['cid'][0]),
                    'lessonArrange': '课程安排'},
                meta=new_meta, # {'item': item},
                callback=self.lesson_parser
            )
        # ret = [__get_req(tr) for tr in trs]
        # for r in ret:
        #     logger.debug(r.meta)
        # return ret

#             yield Request(url=ELECT_URL+'viewLessonArrange.aspx?kcdm='+cid+'&xklx=%e9%80%9a%e8%af%86&redirectForm=speltyCommonCourse.aspx&yxdm=&tskmk=440&kcmk=-1&nj=%e6%97%a0',
#                     dont_filter=True)

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

        trs = response.xpath('//table[@id="LessonTime1_gridMain"]/tr[re:test(@class,"tdcolour\d$")]')
        if not trs: 
            logger.debug(response.meta['item']['cid']+response.meta['item']['name'])
            et_str='gridGModule$ctl'+response.meta['item']['course_type']+'$radioButton'
            return response.request.replace(formdata={et_str: 'radioButton',
                    'myradiogroup': str(response.meta['item']['cid']),
                    'lessonArrange': '课程安排'},
                    )
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
                # yield Request(url=TEST_SHUXUE_URL, 
                #         dont_filter=True, 
                #         meta= {'item':loader.load_item()},
                #         callback = self.renxuan_2
                # )
                new_meta = {'item': loader.load_item()}
                new_meta.update(response.meta)
                req =  FormRequest.from_response(
                        response, 
                        dont_filter=True,
                        formdata = params,
                        meta = new_meta,
                        callback = self.renxuan_2
                )
                yield req

    def renxuan_2(self, response):
        trs = response.xpath('//table[@id="OutSpeltyEP1_gridMain"]/tbody/tr[re:test(@class,"tdcolour\d$")]')
        for tr in trs:
            loader = ItemLoader(response.meta['item'], selector=tr)
            cid = loader.get_xpath('./td[3]/text()')
            loader.add_xpath('name', './td[2]/text()')
            loader.add_xpath('cid', './td[3]/text()')
            loader.add_xpath('credit', './td[6]/text()')
            # yield Request(url=TEST_LESSON_URL, 
            #         dont_filter=True, 
            #         meta= {'item':loader.load_item()},
            #         callback = self.lesson_parser
            # )
            new_meta = {'item': loader.load_item()}
            new_meta.update(response.meta)
            yield FormRequest.from_response(
                    response,
                    dont_filter=True,
                    formdata={
                        'OutSpeltyEP1$dpYx':response.meta['item']['course_type'],
                        'OutSpeltyEP1$dpNj':response.meta['item']['grade'],
                        'myradiogroup':cid,
                        'OutSpeltyEP1$lessonArrange': '课程安排'
                    },
                    meta=new_meta,
                    callback=self.lesson_parser
            )

    def start_requests(self):
         yield Request(ELECT_URL+'speltyCommonCourse.aspx',
            dont_filter=True, 
            callback=self.tongshi_1
        )
         # yield Request(ELECT_URL+'outSpeltyEP.aspx',
         #    dont_filter=True, 
         #    callback=self.renxuan_1
        # )
         # yield Request(ELECT_URL+'electwarning.aspx?xklc=1',
         #         dont_filter=True,
         #         callback=self.test)

    def test(self, response):
        r = FormRequest.from_response(response,
                 url= ELECT_URL+'electwarning.aspx?xklc=1',# TEST_FULL_URL,
                 formdata={'CheckBox1': 'on', 'btnContinue': '继续'},
                 dont_filter=True,
                 callback=self.test)
        yield r

    def __init__(self, username, password):
        self.user = username
        self.passwd = password

#     def test_tongshi(self, response):
#         item = copy.deepcopy(response.meta['item'])
#         trs = response.xpath('//table[@id="gridMain"]/tr[re:test(@class,"tdcolour\d$")]')
#         tr = trs[0]
#         # et_str = 'gridGModule$ctl'+response.meta['item']['course_type']+'$radioButton'
#         item['name'] = tr.xpath('./td[2]/text()').extract_first().strip()
#         # item['cid'] = tr.xpath('./td[3]/text()').extract_first().strip()
#         # item['credit'] = tr.xpath('./td[5]/text()').extract_first().strip()

#         new_meta = copy.deepcopy(response.meta)
#         new_meta.update({'item': copy.deepcopy(item)})

#         req1 = FormRequest.from_response(
#             response, 
#             dont_filter=True,
#             url=ELECT_URL+'speltyCommonCourse.aspx',
#             formdata={},# et_str: 'radioButton',
#                 # 'myradiogroup': str(item['cid']),'lessonArrange': '课程安排'},
#             meta=new_meta, # {'item': item},
#             callback=self.lesson_parser
#         )
#         logger.debug(req1.meta)
#         set_trace()

#         tr = trs[1]
#         item['name'] = tr.xpath('./td[2]/text()').extract_first().strip()
#         # item['cid'] = tr.xpath('./td[3]/text()').extract_first().strip()
#         # item['credit'] = tr.xpath('./td[5]/text()').extract_first().strip()

#         new_meta = copy.deepcopy(response.meta)
#         new_meta.update({'item': copy.deepcopy(item)})
#         # new_meta.update({'item': {'b': '2'}})

#         req2 = FormRequest.from_response(
#             response, 
#             dont_filter=True,
#             url=ELECT_URL+'speltyCommonCourse.aspx',
#             formdata={},# et_str: 'radioButton',
#                 # 'myradiogroup': str(item['cid']),'lessonArrange': '课程安排'},
#             meta=new_meta, # {'item': item},
#             callback=self.lesson_parser
#         )
#         logger.debug('')
#         logger.debug(req1.meta)
#         logger.debug(req2.meta)

