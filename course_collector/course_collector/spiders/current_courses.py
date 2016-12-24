from scrapy import Spider, Item, Field
from scrapy.loader import ItemLoader
from scrapy.http import Request
from course_collector.items import Course, CourseTime
from course_collector.spiders.tongshi import ELECT_URL
from pdb import set_trace
import numpy
import re
import os
from scrapy.shell import inspect_response
from logging import getLogger

TEST_URL = 'http://localhost/ele/website/%E5%BF%AB%E9%80%9F%E9%80%80%E8%AF%BE%E7%95%8C%E9%9D%A2_files/removeLessonFast.html'
TARGET_URL = ELECT_URL+'removeLessonFast.aspx'
RECOMMAND_URL = ELECT_URL+'RecommandTblOuter.aspx'

logger = getLogger(__name__)

class CurrentSpider(Spider):
    name = "current"
    custom_settings = {
            'FEED_URI': 'file://'+os.getcwd()+'/data/current.json',
            'FEED_FORMAT': 'json',
            'FEED__EXPORT_ENCODING': 'utf-8',
            'LOG_LEVEL': 'INFO',
            'MYCOOKIE_ENABLED': True,
            'ITEM_PIPELINES': {'course_collector.pipelines.current.CurrentPipeline': 300}
            }

    # start_urls=[TEST_URL]
    def start_requests(self):
        yield Request(TARGET_URL, dont_filter=True, callback=self.parse)

    # FIXME: MyCookieMiddleware shouldn't need these attributes
    def __init__(self):
        self.user = 'a'
        self.passwd = 'b'

    def parse(self, response):
        def __to_time(info, weekday, cend, cbegin):
            ct = CourseTime()
            ct['weekday'] = weekday
            ct['cend'] = cend
            ct['cbegin'] = cbegin
            ct['wbegin'] = info[1]
            ct['wend'] = info[2]
            return ct

        def parse_table(table):
            ''' ret[7]: 第8个需要记录的课的(行数, 列数)
                需要记录的课在这里被认为是带@rowspan的
            '''
            draft = numpy.zeros((15, 8))
            ret = []
            # ret = [[] for _ in range(15)]
            for row_i, row in enumerate(table):
                for col_i, col in enumerate(row.xpath('./td')):
                    while draft[row_i][col_i]: col_i += 1
                    try:
                        rowspan = int(col.xpath('./@rowspan').extract_first())
                        ret.append((row_i, col_i))
                    except TypeError:
                        rowspan = 1
                    for i in range(rowspan):
                        draft[row_i + i][col_i] = rowspan-i
                    # ret[row_i].append(col_i)
            return ret

        # inspect_response(response, self)
        parse_result = parse_table(response.css('table.alltab tr'))

        courses = {}
        for tr_i, tr in enumerate(response.css('td.classmain[rowspan]')):
            weekday = '一二三四五六日'[parse_result[tr_i][1]-1]
            cbegin = parse_result[tr_i][0]
            cend = cbegin + int(tr.xpath('./@rowspan').extract_first())-1
            s = '\n'.join(tr.css('::text').extract())

            both=re.findall('(.*)\s*(?:\(|（)(\d+)-(\d+)周(?:\)|）)\s*(?:\[(\w+\d*)\])?(?!\s*(?:单周|双周))', s)
            odds=re.findall('(.*)\s*(?:\(|（)(\d+)-(\d+)周(?:\)|）)\s*(?:\[(\w+\d*)\])?(?=\s*(?:单周))', s)
            evens=re.findall('(.*)\s*(?:\(|（)(\d+)-(\d+)周(?:\)|）)\s*(?:\[(\w+\d*)\])?(?=\s*(?:双周))', s)
            odds += both
            evens += both
            logger.info(odds)
            logger.info(evens)

            for odd in odds:
                try:
                    courses[odd[0]]['odd_week'].append(__to_time(odd, weekday, cend, cbegin))
                except KeyError:
                    courses[odd[0]] = {'name': odd[0], 'place': odd[3],
                        'odd_week':[], 'even_week': []}
                    courses[odd[0]]['odd_week'].append(__to_time(odd, weekday, cend, cbegin))
            for even in evens:
                try:
                    courses[even[0]]['even_week'].append(__to_time(even, weekday, cend, cbegin))
                except KeyError:
                    courses[even[0]] = {'name': even[0], 'place': even[3],
                        'odd_week':[], 'even_week': []}
                    courses[even[0]]['even_week'].append(__to_time(even, weekday, cend, cbegin))
        set_trace()
        for course in courses.values():
            yield course
