#! /usr/bin/env python3
from jaccount import login
from pdb import set_trace
from bs4 import BeautifulSoup
import requests
from itertools import count

# TODO:
#   1. Try to grab courses directly.(not step by step from main page)

# When in main page (aka path /)
TARGET_URL = 'http://electsys.sjtu.edu.cn/edu/'
ASP_FORM_ID = ['__VIEWSTATE', '__VIEWSTATEGENERATOR', '__EVENTVALIDATION']
def autition(sess):
    # Get this site also work ???
    # http://electsys.sjtu.edu.cn/edu/student/elect/electcheck.aspx?xklc=1
    # resp = sess.post(xkurl, data = prepare_form('?xklc=1'))
    # Can I do not assign sess?
    sess, resp = crowd_into_main(sess, query = '?xklc=1')
    print(resp.text)
    set_trace()

def crowd_into_main(sess, query):
    # query = '?xklc=1': 海选
    # query = '?xklc=2': 抢选
    # query = '?xklc=3': 第三轮选
    # The same as clicking '海选' in the main page
    # Speed: about 25 posts per second when the server is not busy
    # TODO:  
    #   1. Throw exception when __EVENTVALIDATION is out of date
    #   2. Get /edu/student/elect/electcheck.aspx?xklc=1 directly may work
    #       resp = sess.get(TARGET_URL+'student/elect/electcheck.aspx'+query)
    #   3. Abort redirection when next url '对不起' to promote speed
    #       resp = sess.post(xkurl, data = form, allow_redirects = False)
    #       while resp.status_code != 200 and '%e5%af%b9%e4%b8%8d%e8%b5%b7%2c' not in resp.url:
    #           print(resp.url)
    #           resp = sess.get(resp.url, allow_redirects = False)
    '对不起,你目前不能进行该轮选课'
    '''%e5%af%b9%e4%b8%8d%e8%b5%b7%2c%e4%bd%a0%e7%9b%ae%e5%89%8d%e4%b8%8d\
        %e8%83%bd%e8%bf%9b%e8%a1%8c%e8%af%a5%e8%bd%ae%e9%80%89%e8%af%be'''
    xkurl = TARGET_URL+'student/elect/electwarning.aspx'
    form = prepare_form(sess, query)
    while True:
        try:
            # if any item of asp.net form missing we will get electwarning.aspx
            assert len(form) >= 5
            resp = sess.post(xkurl, data = form)
            resp.raise_for_status()
            if '%e5%af%b9%e4%b8%8d%e8%b5%b7%2c' not in resp.url:
                return sess, resp
        except requests.exceptions.HTTPError:
            print('Form updated')
            form = prepare_form(sess, query)

    ''' For debugging purpose'''
    # for i in count():
    #     resp = sess.post(xkurl, data = form)
    #     if '%e5%af%b9%e4%b8%8d%e8%b5%b7%2c' not in resp.url:
    #         return sess

    #     if not i%100:
    #         print('Trying to login for ' + str(i) + ' times')
    #     if not i % 500 and i != 0:
    #         set_trace()

def asp_form(sess, url):
    soup = BeautifulSoup(sess.get(url).text, 'html.parser')
    return {inp['name']: inp['value'] for inp in soup.find_all('input') if
            inp['name'] in ASP_FORM_ID}

# update ASP.NET validation
def prepare_form(sess, query):
    # Also work if don't pass sess in when 海选
    form = asp_form(sess, TARGET_URL+'student/elect/electwarning.aspx'+query)
    form['CheckBox1'] = 'on'
    form['btnContinue'] = '继续'
    return form
    # order elements if needed
    # return [(s, form[s]) for s in ['__VIEWSTATE', '__VIEWSTATEGENERATOR', 
    #   '__EVENTVALIDATION', 'CheckBox1', 'btnContinue']]

    # form_url = 'http://electsys.sjtu.edu.cn/edu/newsboard/newsinside.aspx'

def prepare_cookie(sess):
    ele_cookies_list = ['ASP.NET_SessionId', 'mail_test_cookie']
    return {s: sess.cookies[s] for s in ele_cookies_list}

if __name__ == '__main__':
    sess = login('zxdewr', 'sszh2sc')
    autition(sess)
