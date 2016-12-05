import logging
from six.moves.urllib.parse import urljoin
from scrapy.shell import inspect_response
from pdb import set_trace
from urllib.parse import urlparse, unquote
from scrapy.downloadermiddlewares.redirect import RedirectMiddleware

from w3lib.url import safe_url_string

from scrapy.http import HtmlResponse, FormRequest, Response
from scrapy.utils.response import get_meta_refresh
from scrapy.exceptions import IgnoreRequest, NotConfigured

logger = logging.getLogger(__name__)

class MyRedirectMiddleware(RedirectMiddleware):
    ''' This middleware is used to recover original post request when redirected
        to either the message page or the outTimePage.aspx.
    '''

    def _recover_post(self, request):
        try:
            return request.replace(url=request.meta['redirect_urls'][0],
                    body=request.meta['post_body'],
                    method='POST'
            )
        # These exceptions should not happen in my project.
        # Switch the logger level 'error' to 'debug' when you use it.
        except IndexError:
            logger.error("Request has no redirection record.")
            raise IgnoreRequest("Request has no redirection record.")
        except KeyError:
            logger.error("No form data recorded")
            raise IgnoreRequest("No form data recorded")

    def process_response(self, request, response, spider):
        # TODO: Delete the outdated cookie
        if urlparse(request.url).path.split('/')[-1] == 'outTimePage.aspx':
            logger.debug('Cookie %s is out of date.' % request.cookies)
            return self._recover_post(request)

        if 'message=' in request.url:
            logger.debug(unquote(request.url).split('message=')[1])
            return self._recover_post(request)

        ret = RedirectMiddleware.process_response(self, request, response, spider)

        # Record data to be posted
        if response.status == 302 and isinstance(request, FormRequest):
            ret.meta['post_body'] = request.body

        return ret

# class BaseRedirectMiddleware(object):

#     enabled_setting = 'REDIRECT_ENABLED'

#     def __init__(self, settings):
#         if not settings.getbool(self.enabled_setting):
#             raise NotConfigured

#         self.max_redirect_times = settings.getint('REDIRECT_MAX_TIMES')
#         self.priority_adjust = settings.getint('REDIRECT_PRIORITY_ADJUST')

#     @classmethod
#     def from_crawler(cls, crawler):
#         return cls(crawler.settings)

#     def _redirect(self, redirected, request, spider, reason):
#         ttl = request.meta.setdefault('redirect_ttl', self.max_redirect_times)
#         redirects = request.meta.get('redirect_times', 0) + 1

#         if ttl and redirects <= self.max_redirect_times:
#             if isinstance(request, FormRequest):
#                 redirected.meta['post_body'] = request.body
#             redirected.meta['redirect_times'] = redirects
#             redirected.meta['redirect_ttl'] = ttl - 1
#             redirected.meta['redirect_urls'] = request.meta.get('redirect_urls', []) + \
#                 [request.url]
#             redirected.dont_filter = request.dont_filter
#             redirected.priority = request.priority + self.priority_adjust
#             logger.debug("Redirecting (%(reason)s) to %(redirected)s from %(request)s",
#                          {'reason': reason, 'redirected': redirected, 'request': request},
#                          extra={'spider': spider})
#             return redirected
#         else:
#             logger.debug("Discarding %(request)s: max redirections reached",
#                          {'request': request}, extra={'spider': spider})
#             raise IgnoreRequest("max redirections reached")

#     def _redirect_request_using_get(self, request, redirect_url):
#         redirected = request.replace(url=redirect_url, method='GET', body='')
#         redirected.headers.pop('Content-Type', None)
#         redirected.headers.pop('Content-Length', None)
#         return redirected

#     def _recover_post(self, request):
#         try:
#             return request.replace(url=request.meta['redirect_urls'][0],
#                     body=request.meta['post_body'],
#                     method='POST'
#             )
#         except IndexError:
#             raise IgnoreRequest("Request has no redirection record.")


# class RedirectMiddleware(BaseRedirectMiddleware):
#     """Handle redirection of requests based on response status and meta-refresh html tag"""

#     def process_response(self, request, response, spider):
#         # if request.meta.get('redirect_urls', []):
#         # # if response.status == 302:
#         #     set_trace()
#         #     # inspect_response(response, spider)
#         if (request.meta.get('dont_redirect', False) or
#                 response.status in getattr(spider, 'handle_httpstatus_list', []) or
#                 response.status in request.meta.get('handle_httpstatus_list', []) or
#                 request.meta.get('handle_httpstatus_all', False)):
#             return response

#         # TEST
#         # TODO: Delete the outdated cookie
#         if urlparse(request.url).path.split('/')[-1] == 'outTimePage.aspx':
#             logger.debug('Cookie %s is out of date.' % request.cookies)
#             return self._recover_post(request)

#         allowed_status = (301, 302, 303, 307)
#         if 'Location' not in response.headers or response.status not in allowed_status:
#             return response

#         location = safe_url_string(response.headers['location'])

#         redirected_url = urljoin(request.url, location)

#         if response.status in (301, 307) or request.method == 'HEAD':
#             redirected = request.replace(url=redirected_url)
#             return self._redirect(redirected, request, spider, response.status)

#         redirected = self._redirect_request_using_get(request, redirected_url)
#         return self._redirect(redirected, request, spider, response.status)


# class MetaRefreshMiddleware(BaseRedirectMiddleware):

#     enabled_setting = 'METAREFRESH_ENABLED'

#     def __init__(self, settings):
#         super(MetaRefreshMiddleware, self).__init__(settings)
#         self._maxdelay = settings.getint('REDIRECT_MAX_METAREFRESH_DELAY',
#                                          settings.getint('METAREFRESH_MAXDELAY'))

#     def process_response(self, request, response, spider):
#         if request.meta.get('dont_redirect', False) or request.method == 'HEAD' or \
#                 not isinstance(response, HtmlResponse):
#             return response

#         if isinstance(response, HtmlResponse):
#             interval, url = get_meta_refresh(response)
#             if url and interval < self._maxdelay:
#                 redirected = self._redirect_request_using_get(request, url)
#                 return self._redirect(redirected, request, spider, 'meta refresh')

#         return response
