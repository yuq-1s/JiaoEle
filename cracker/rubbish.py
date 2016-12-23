# class course(object):
#     def __init__(self, **kwargs):
#         self.cid = kwargs['cid']
#         self.bsid = kwargs['bsid']
#         self.xyid = kwargs['xyid']

# def autition(sess):
#     # Get this site also work ???
#     # http://electsys.sjtu.edu.cn/edu/student/elect/electcheck.aspx?xklc=1
#     # resp = sess.post(xkurl, data = prepare_form('?xklc=1'))
#     # Can I do not assign sess?
#     # sess, form = init(sess, query='?xklc=1')
#     return init(sess, query='?xklc=1')

# def prepare_cookie(sess):
#     ele_cookies_list = ['ASP.NET_SessionId', 'mail_test_cookie']
#     return {s: sess.cookies[s] for s in ele_cookies_list}

# def check_form(recover_url):
#     logger = logging.getLogger(__name__)
#     asp = asp_form(sess.get(recover_url).text)
#     form.update(asp)
#     def decorator(f):
#         @wraps(f)
#         def wrapper(sess, form):
#             try:
#                 return f(sess, form)
#             except requests.exceptions.HTTPError:
#                 logger.warn('ASP params are wrong. Trying another time...')
#                 asp = asp_form(sess.get(recover_url).text)
#                 return f(sess, form.update(asp))
#             raise RuntimeError('Fetching ASP params failed')
#         return wrapper
#     return decorator


# def until(is_okay):
#     def decorator(f):
#         @wraps(f)
#         def wrapper(*args):
#             result = f(*args)
#             for cnt in count():
#                 logger.debug(f.__name__ + ' failed the ' + cnt ' times.')
#                 if is_okay(result):
#                     break
#                 result = f(*args)
#             return result
#         return wrapper
#     return decorator


# @until(lambda url: '%e5%af%b9%e4%b8%8d%e8%b5%b7%2c' not in url)
# @check_form(ELECT_URL+'speltyCommonCourse.aspx', {'btnSubmit', '选课提交'})
# def do_submit(sess, form):
#     resp = sess.post(ELECT_URL+'electwarning.aspx', data=form)
#     resp.raise_for_status()
#     return resp.url

# def init(sess, query):
#     # The same as clicking '海选' in the main page
#     # Speed: about 25 posts per second when the server is not busy
#     # TODO:
#     #   1. Throw exception when __EVENTVALIDATION is out of date
#     #   2. Get /edu/student/elect/electcheck.aspx?xklc=1 directly may work
#     #       resp = sess.get(TARGET_URL+'student/elect/electcheck.aspx'+query)
#     #   3. Abort redirection when next url '对不起' to promote speed
#     #       resp = sess.post(xkurl, data = form, allow_redirects = False)
#     #       while resp.status_code != 200 and '%e5%af%b9%e4%b8%8d%e8%b5%b7%2c' not in resp.url:
#     #           print(resp.url)
#     #           resp = sess.get(resp.url, allow_redirects = False)
#     '对不起,你目前不能进行该轮选课'
#     '''%e5%af%b9%e4%b8%8d%e8%b5%b7%2c%e4%bd%a0%e7%9b%ae%e5%89%8d%e4%b8%8d\
#         %e8%83%bd%e8%bf%9b%e8%a1%8c%e8%af%a5%e8%bd%ae%e9%80%89%e8%af%be'''
#     xkurl = ELECT_URL + 'electwarning.aspx'
#     form = prepare_form(sess, query)
#     while True:
#         try:
#             # if any item of asp.net form missing we will get electwarning.aspx
#             assert len(form) >= 5
#             resp = sess.post(xkurl, data=form)
#             resp.raise_for_status()
#             if '%e5%af%b9%e4%b8%8d%e8%b5%b7%2c' not in resp.url:
#                 return sess, asp_form(resp.text)
#             else:
#                 print('Trying to crowd into main')
#         except requests.exceptions.HTTPError:
#             print('Updating form...')
#             form = prepare_form(sess, query)

#     ''' For debugging purpose'''
#     # for i in count():
#     #     resp = sess.post(xkurl, data = form)
#     #     if '%e5%af%b9%e4%b8%8d%e8%b5%b7%2c' not in resp.url:
#     #         return sess

#     #     if not i%100:
#     #         print('Trying to login for ' + str(i) + ' times')
#     #     if not i % 500 and i != 0:
#     #         set_trace()


# # update ASP.NET validation
