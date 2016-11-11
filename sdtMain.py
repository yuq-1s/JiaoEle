#! /usr/bin/env python3
from jaccount import login
from pdb import set_trace
from bs4 import BeautifulSoup
import requests

# When in main page (aka path /)
TARGET_URL = 'http://electsys.sjtu.edu.cn/edu/'
ASP_FORM_ID = ['__VIEWSTATE', '__VIEWSTATEGENERATOR', '__EVENTVALIDATION']
def autition(sess):
    # xklc = 1: 海选
    # xklc = 2: 抢选
    # xklc = 3: 第三轮选
    xkurl = TARGET_URL+'student/elect/electwarning.aspx'+'?xklc=1'

    # Get this site also work ???
    # http://electsys.sjtu.edu.cn/edu/student/elect/electcheck.aspx?xklc=1
    resp = sess.post(xkurl, data = prepare_form('?xklc=1'))

def prepare_form(query_str):
    sess = requests.Session()
    form_url = TARGET_URL + 'student/elect/electwarning.aspx' + query_str
    form_soup = BeautifulSoup(sess.get(form_url).text, 'html.parser')
    form = {inp['name']: inp['value'] for inp in form_soup.find_all('input') if
            inp['name'] in ASP_FORM_ID}
    form['CheckBox1'] = 'on'
    form['btnContinue'] = '继续'
    assert len(form) == 5
    return [(s, form[s]) for s in ['__VIEWSTATE', '__VIEWSTATEGENERATOR', 
        '__EVENTVALIDATION', 'CheckBox1', 'btnContinue']]

    # form_url = 'http://electsys.sjtu.edu.cn/edu/newsboard/newsinside.aspx'

def prepare_cookie(sess):
    ele_cookies_list = ['ASP.NET_SessionId', 'mail_test_cookie']
    return {s: sess.cookies[s] for s in ele_cookies_list}

if __name__ == '__main__':
    sess = login('username', 'secret')
    autition(sess)
