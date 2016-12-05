from pdb import set_trace
from scrapy.http import Request
from scrapy.item import BaseItem
from scrapy.shell import inspect_response
from scrapy.exceptions import NotConfigured
from scrapy import signals
from jaccount import login
from time import time
from copy import deepcopy
import queue
import logging

# TODO: schedule post requests until get page without message in url
# TODO: MAX_COOKIE_NUMBER
class MyCookieMiddleware(object):
    # PARAM_URLS = {'tongshi': EDU_URL+'elect/speltyCommonCourse.aspx',
    #         'renxuan': EDU_URL+'elect/outSpeltyEP.aspx',
    #         'kecheng': EDU_URL+'lesson/viewLessonArrange.aspx/'
    #         }
    # ASP_FORM_ID = ['__VIEWSTATE', '__VIEWSTATEGENERATOR', '__EVENTVALIDATION',
    #         '__EVENTARGUMENT', '__LASTFOCUS']
    MIN_DELTA = 2
    logger = logging.getLogger(__name__)

    class TimedCookie(object):
        def __init__(self, cookie):
            self.cookie = cookie
            self.last_used = time()

    @classmethod
    def from_crawler(cls, crawler):
        s = crawler.settings
        if not s.getbool('MYCOOKIE_ENABLED'):
            raise NotConfigured
        user = crawler.spider.user
        passwd = crawler.spider.passwd
        o = cls(user, passwd)
        # TODO: signal???
        return o

    def __init__(self, user, password):
        self.user = user
        self.passwd = password
        self.cookie_queue = queue.Queue()
        self.cookie_queue.put(self.TimedCookie(self._new_cookie()))
        self.logger.debug('CookieQueue middleware start')

    # HACK: login() should be intended to get more cookies at a time.
    def _new_cookie(self):
        wanted = ['ASP.NET_SessionId', 'mail_test_cookie']
        return {'ASP.NET_SessionId': 'laxxrayahzgsow45idrlnl2i',
                'mail_test_cookie': 'IHIBHIAK'}
        # return {s: login(self.user, self.passwd).cookies[s] for s in wanted}

    def _get(self):
        while True:
            try:
                timed_cookie = self.cookie_queue.get()
                # set_trace()
                if time() - timed_cookie.last_used >= self.MIN_DELTA:
                    return timed_cookie.cookie
                else:
                    self.cookie_queue.put(timed_cookie)
                    # if not self.cookie_queue.full():
                    #     self.logger.debug('Fetching new cookie...')
                    #     return self._new_cookie()
            except cookie_queue.Empty:
                self.logger.debug('Fetching new cookie...')
                return self._new_cookie()

    def _put(self, cookie):
        self.cookie_queue.put(self.TimedCookie(cookie))

    def process_spider_output(self, response, result, spider):
        # inspect_response(response, spider)
        if 'message' in response.url:
            self.logger.debug('Getting message url')
            set_trace()
            return (response.request,)

        for r in result:
            # TODO: Take care of GET requests
            if isinstance(r, Request):
                self.logger.debug('Processing request %s...' % r)
                cookie = self._get()
                self._put(cookie)
                assert 'ASP.NET_SessionId' in r.replace(cookies=cookie).cookies
                yield r.replace(cookies = cookie)
            else:
                yield r

#     def update_param(self):
#         for page_name, url in PARAM_URLS.items():
#             soup = BeautifulSoup(requests.get(url, cookies = self.cookies).text,
#                     'html.parser')
#             param_dict[page_name] = {inp['name']: inp['value']
#                     for inp in soup.find_all('input')
#                     if inp['name'] in ASP_FORM_ID
#                     }

# TODO: Make a pool of cookies and asp_values
# TODO: Add Exception handling: if '对不起' in resp.url: yield response.request
# class AspSession(object):
#     logger = getLogger()
#     def __init__(self, username, password):
#         self._sess = login(username, password)
#         self.cookies = self._get_cookie()
#         self.params = self._get_params()

#     # TODO: Update a specific page's asp_param
#     def update_params(self):
#         self.logger.info('updating asp params...')
#         self.params = self._get_params(_sess)


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