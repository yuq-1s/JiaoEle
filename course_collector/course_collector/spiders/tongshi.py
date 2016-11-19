#! /usr/bin/env python
# -*- coding: utf-8 -*-

from scrapy import Spider, FormRequest, Request
from jaccount import login
from pdb import set_trace

class TongShi(Spider):
    name = 'tongshi'
    # def prepare_param(self, response, xyid = None):
    #     # ASP_PARA_LIST = ['__VIEWSTATE', '__VIEWSTATEGENERATOR',
    #     # '__EVENTVALIDATION']
    #     param_path = response.xpath('//input[re:test(@name, "__[A-Z]+")]')
    #     params = {n:v for n in param_path.xpath('./@name') 
    #             for v in param_path.xpath('./@value')}
    #     params['gridGModule$ctl' + xyid + '$radioButton'] = 'radioButton' # ???
    #     params['__EVENTTARGET'] = 'gridGModule$ctl' + xyid + '$radioButton'

    def parse(self, response):
        # set_trace()
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)
        return [FormRequest.from_response(response, 
            formdata = {'CheckBox1': 'on', 'btnContinue' : '继续'},
            callback = self.after_post
        )]

    def after_post(self, response):
        if '%e5%af%b9%e4%b8%8d%e8%b5%b7%2c' in response.url:
            return
            [Request('file:///home/yuq/Documents/sjtu/electsys/website/通识课_files/speltyCommonCourse.html',
                callback=self.parse_tongshi)]

    def parse_tongshi(self, response):
        courses = response.xpath('//table[@id="gridMain"]/tbody/tr[re:test(@class, "tdcolour\d$")]')
        from scrapy.shell import inspect_response
        inspect_response(response, self)

    def start_requests(self):
        requests = Request('http://electsys.sjtu.edu.cn/edu/student/elect/electwarning.aspx',
            cookies = login('zxdewr', 'sszh2sc'), 
            dont_filter=True, 
            callback=self.parse
        )

        if type(requests) is list:
            for request in requests:
                yield request
        else:
            yield requests


