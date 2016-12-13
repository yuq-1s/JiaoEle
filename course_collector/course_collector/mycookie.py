from pdb import set_trace
from scrapy.http import Request, FormRequest
from scrapy.item import BaseItem
from scrapy.shell import inspect_response
from scrapy.exceptions import NotConfigured
from scrapy import signals
from urllib.parse import urlparse
from jaccount import login
from time import clock, sleep
from copy import deepcopy
from threading import get_ident
import queue
import logging

logger = logging.getLogger(__name__)
usage_update = 0

# TODO: Store cookies for futher usage.
# TODO: @property may help?
class TimedCookie(object):
    def __init__(self, cookie):
        self.cookie = cookie
        self.last_used = clock()
        if not cookie.get('usage_count', False):
            global usage_update
            self.cookie['usage_count'] = usage_update
        # if not cookie.get('id', False):
        #     # set_trace()
        #     # logger.debug(cookie_count)
        #     global cookie_count
        #     self.cookie['id'] = cookie_count
        #     cookie_count += 1
            # logger.debug(self._cookie_count)
        # self.id = self._cookie_count
        # self._cookie_count += 1
        # logger.debug("Total: %d"%self._cookie_count)

    def __lt__(self, other):
        return self.cookie.get('usage_count', 0) < other.cookie.get('usage_count', 0)
        # return self.last_used < other.last_used

# TODO: schedule post requests until get page without message in url
# TODO: MAX_COOKIE_NUMBER
class MyCookieMiddleware(object):
    # PARAM_URLS = {'tongshi': EDU_URL+'elect/speltyCommonCourse.aspx',
    #         'renxuan': EDU_URL+'elect/outSpeltyEP.aspx',
    #         'kecheng': EDU_URL+'lesson/viewLessonArrange.aspx/'
    #         }
    # ASP_FORM_ID = ['__VIEWSTATE', '__VIEWSTATEGENERATOR', '__EVENTVALIDATION',
    #         '__EVENTARGUMENT', '__LASTFOCUS']
    MIN_DELTA = 0.1
    QUEUE_SIZE = 1

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

    def inspect_queue(self):
        lst = []
        while not self.cookie_queue.empty():
            lst.append(self.cookie_queue.get())
            self.cookie_queue.task_done()
        print(len(lst))
        for thing in lst:
            self.cookie_queue.put(thing)


    def __init__(self, user, password):
        self.user = user
        self.passwd = password
        # SPIDERS ARE USING THEIR OWN COOKIE_QUEUES............
        self.cookie_count = 0
        self.cookie_queue = queue.PriorityQueue()
        self.__normal_cookie = self._new_cookie()
        # del(self.__normal_cookie['id'])
        self.need_recycle = set()
        # logger.debug('CookieQueue middleware start')

    # HACK: login() should be intended to get more cookies at a time.
    def _new_cookie(self):
        # self.cookie_count += 1
        # self.board.append(min(self.board)+1)
        # logger.info('Fetching new cookie... Total: %d' % self.cookie_count)
        logger.debug('New Cookie')
        # sleep(0.2)
        wanted = ('ASP.NET_SessionId', 'mail_test_cookie')
        cookie =  {'ASP.NET_SessionId': 'mikay2imywwyto55ykfpxa45',
                'mail_test_cookie': 'IHIBHIAK', 'id': self.cookie_count}
        # with open('cookies.txt', 'a') as f:
        #     f.write(cookie)
        #     f.write('\n')
        self.cookie_count += 1
        return cookie
        # return {s: login(self.user, self.passwd).cookies[s] for s in wanted}

    def _get_post_cookie(self):
        while True:
            try:
                timed_cookie = self.cookie_queue.get(timeout = self.MIN_DELTA)# _nowait()
                self.cookie_queue.task_done()
                # logger.debug(timed_cookie.cookie)
                # logger.debug("ID: %d" % timed_cookie.cookie['id'])
                delta = clock() - timed_cookie.last_used
                if delta >= self.MIN_DELTA:
                    timed_cookie.cookie['usage_count'] += 1
                    logger.debug("Usage Count %d"%timed_cookie.cookie['usage_count'])
                    return timed_cookie.cookie
                else:
                    self.cookie_queue.put(timed_cookie)
                    global usage_update
                    usage_update = timed_cookie.cookie['usage_count']
                    # logger.debug("update: %d" % usage_update)
                    if self.cookie_count < 20:
                        return self._new_cookie()
                # inspect_queue(self.cookie_queue)
            except queue.Empty:
                return self._new_cookie()
    def _get_other_cookie(self):
        return self.__normal_cookie
        # try:
        #     cookie = self.cookie_queue.get(timeout = self.MIN_DELTA)# _nowait().cookie
        #     self.cookie_queue.task_done()
        #     return cookie
        # except queue.Empty:
        #     return self._new_cookie()

    def _put(self, cookie):
        # self.inspect_queue()
        if cookie['id'] in self.need_recycle:
            logger.debug("Restoring: %d" % cookie['id'])
            timed_cookie = TimedCookie(cookie)
            self.cookie_queue.put(timed_cookie)
            self.inspect_queue()
            self.need_recycle.remove(cookie['id'])

    def _get(self, request):
        if request.method == 'POST':
            cookie = self._get_post_cookie()
            self.need_recycle.add(cookie['id'])
        else:
            cookie = self._get_other_cookie()
        return cookie

    def process_request(self, request, spider):
        if not request.headers['Referer']==b'http://electsys.sjtu.edu.cn/edu/student/elect/speltyCommonCourse.aspx':
            set_trace()
        if request.cookies:    return

        # TODO: Take care of GET requests
        # logger.debug('processing request %s...' % request)
        cookie = self._get(request)
        # assert 'asp.net_sessionid' in request.replace(cookies=cookie).cookies
        return request.replace(cookies = cookie)

    def process_response(self, request, response, spider):
        # if not self.cookie_queue.empty():
        #     self.cookie_queue.task_done()

        # FIXME: Decrease cookie_count when outdated
        if urlparse(request.url).path.split('/')[-1] != 'outTimePage.aspx':
            # logger.debug("usage_count: %d" % request.cookies.get('usage_count', 0))
            # if request.method == 'POST':
            #     logger.debug(request)
            # pass
            self._put(request.cookies)
            # inspect_queue(self.cookie_queue)
        else:
            # self.cookie_count -= 1
            logger.info('Cookie %s is out of date.' % request.cookies)
            response.cookies = self._get(request)
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
#         logger.info('updating asp params...')
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
