from pdb import set_trace
from scrapy.http import Request
from scrapy.item import BaseItem
from scrapy.shell import inspect_response
from scrapy.exceptions import NotConfigured
from scrapy import signals
from urllib.parse import urlparse
from jaccount import login
from time import time, sleep
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
    MIN_DELTA = 5
    logger = logging.getLogger(__name__)
    # cookie_queue = queue.Queue()
    # logger.setLevel('INFO')

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
        cqueue = crawler.spider.cqueue
        o = cls(user, passwd, cqueue)
        # TODO: signal???
        return o

    def __init__(self, user, password, cqueue):
        self.user = user
        self.passwd = password
        self.cookie_count = 0
        # SPIDERS ARE USING THEIR OWN COOKIE_QUEUES............
        self.cookie_queue = cqueue
        self.cookie_queue[0].put(self.TimedCookie(self._new_cookie()))
        self.logger.debug('CookieQueue middleware start')

    # HACK: login() should be intended to get more cookies at a time.
    def _new_cookie(self):
        self.cookie_count += 1
        self.logger.info('Fetching new cookie... Total: %d' % self.cookie_count)
        wanted = ('ASP.NET_SessionId', 'mail_test_cookie')
        # return {'ASP.NET_SessionId': 'snx3fqmdztwx0a453uys3f55',
        #         'mail_test_cookie': 'IHIBHIAK'}
        cookie = {s: login(self.user, self.passwd).cookies[s] for s in wanted}
        self.logger.info(cookie)
        return cookie

    def _get_post_cookie(self):
        while True:
            # self.logger.debug('Looping...')
            try:
            # if not self.cookie_queue[0].empty():
                timed_cookie = self.cookie_queue[0].get_nowait()
                # set_trace()
                if time() - timed_cookie.last_used >= self.MIN_DELTA:
                    self.logger.debug(time() - timed_cookie.last_used)
                    self.logger.debug(self.cookie_count)
                    return timed_cookie.cookie
                else:
                    sleep(0.6)
                    self.cookie_queue[0].put(timed_cookie)
                    continue
                    # if not self.cookie_queue[0].full():
                    #     self.logger.debug('Fetching new cookie...')
                    #     return self._new_cookie()
            except queue.Empty:
                return self._new_cookie()

    def _get_other_cookie(self):
        try:
            return self.cookie_queue[0].get_nowait().cookie
        except queue.Empty:
            return self._new_cookie()

    def _put(self, cookie):
        self.cookie_queue[0].task_done()
        self.cookie_queue[0].put(self.TimedCookie(cookie))

    def process_request(self, request, spider):
        # inspect_response(response, spider)
        # if 'message' in response.url:
        #     self.logger.debug('Getting message url')
        #     set_trace()
        #     return (response.request,)

        if request.cookies: 
            # self.logger.debug(str(request.cookies))
            return

        # TODO: Take care of GET requests
        self.logger.debug('processing request %s...' % request)
        cookie = self._get_post_cookie() if request.method == 'POST' else \
            self._get_other_cookie()
        # self._put(cookie)
        # assert 'asp.net_sessionid' in request.replace(cookies=cookie).cookies
        return request.replace(cookies = cookie)

    def process_response(self, request, response, spider):
        if urlparse(request.url).path.split('/')[-1] != 'outTimePage.aspx':
            self._put(request.cookies)
        else:
            self.cookie_count -= 1
            self.logger.info('Cookie %s is out of date.' % request.cookies)
        return response

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
