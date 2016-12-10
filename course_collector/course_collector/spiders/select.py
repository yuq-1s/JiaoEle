from scrapy import Spider
from scrapy.http import Request, FormRequest
from course_collector.spiders.tongshi import LESSON_URL
from logging import getLogger

logger = getLogger(__name__)

class SelectSpider(Spider):
    name = 'select'
    def __init__(self, course):
        self.course = course
        # Is tongshi course
        if self.course.course_type in ['02', '03', '04', '05']:
            query = {'kcdm': self.course.cid,
                    'xklx': '通识',
                    'redirectForm': 'speltyCommonCourse.aspx',
                    'yxdm': None,
                    'tskmk': 420,
                    'kcmk': -1,
                    'nj': '无'
                    }
            self.params = {'myradiogroup': self.course.bsid,
                    '__EVENTTARGET':
                        'gridGModule$ctl%d$radioButton'%self.course.course_type,
                    'LessonTime1$btnChoose': '选定此教师'
                    }
        else:
            query = {'kcdm': self.course.cid,
                    'xklx': '选修',
                    'redirectForm': 'outSpeltyEp.aspx',
                    'yxdm': self.course.course_type,
                    # FIXME: nj may vary
                    'nj': 2015,
                    'kcmk':-1,
                    'txkmk': -1
                    }
            self.params = {'myradiogroup': self.course.bsid,
                    'LessonTime1$btnChoose': '选定此教师'
                    }
        self.url = LESSON_URL+'viewLessonArrange.aspx?'+urlencode(query)

    def start_requests(self):
        yield Request(url=self.url, dont_filter=True, callback=self.select)

    def select(self, response):
        yield FormRequest.from_response(response,
                 formdata=self.params,
                 dont_filter=True,
                 callback=self.submit
                 )

    def submit(self, response):
        yield FormRequest.from_response(response,
                formdata={'btnSubmit', '选课提交'},
                dont_filter=True)
        logger.critical('Course %s got!'%response.meta['self.course_name'])
