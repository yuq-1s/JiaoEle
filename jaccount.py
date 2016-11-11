#! /usr/bin/env python3

'''
    Login jaccount and return requests.session object.

    TODO: 
        1. Add argparse to process username and password from CLI
        2. Decode captcha automatically
'''

import requests
import shutil
import sys
from pdb import set_trace
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

def tohttps(oriurl):
    prot, body = resp.request.url.split(':')
    return prot + 's' + body

def captcha_src(soup):
    for img_tag in soup.findAll('img'):
        if img_tag['src'].startswith('captcha?'):
            return img_tag['src']
    raise RuntimeError("Cannot find captcha.")


def input_captcha(sess, soup):
    r = sess.get('https://jaccount.sjtu.edu.cn/jaccount/'+captcha_src(soup),
            stream=True)
    img = Image.open(BytesIO(r.content))
    img.show()
    return input('What\'s in the image?\n')

def post_data(sess, soup, user, secret):
    form = ['sid', 'returl', 'se', 'v']

    data = dict(zip(form, [soup.find('input', {'name': s}).get('value') for s in form]))
    data['user'] = user
    data['pass'] = secret
    data['captcha'] = input_captcha(sess, soup)
    return data

def login(user, secret):
    # Get Session object
    sess = requests.Session()

    # Store ASP.NetSessionId in sess
    resp = sess.get('http://electsys.sjtu.edu.cn/edu/login.aspx')

    # Prepare for post
    soup = BeautifulSoup(resp.text, 'html.parser')
    post_url = 'https://jaccount.sjtu.edu.cn/jaccount/ulogin'
    
    # Post username and password and get authorization url
    auth_resp = sess.post(post_url, data = post_data(sess, soup, user, secret))
    soup = BeautifulSoup(auth_resp.text, 'html.parser')
    auth_url = soup.find('meta', {'http-equiv':'refresh'})['content'].split('url=')[1]

    # Get authorized
    sess.get(auth_url)

    return sess# , prepare_form(sess)

# def check_session(sess):
#     check_list = ['ASP.NET_SessionId', 'JASiteCookie', 'mail_test_cookie']
#     set_trace()
#     resp_check = sess.get('http://electsys.sjtu.edu.cn/edu/student/sdtinfocheck.aspx',
#             cookies = {s: sess.cookies[s] for s in check_list})
#     set_trace()
# def prepare_form(sess):
#     form_url = 'http://electsys.sjtu.edu.cn/edu/newsboard/newsinside.aspx'
#     form_soup = BeautifulSoup(sess.get(form_url).text, 'html.parser')
#     return {inp['name']: inp['value'] for inp in form_soup.find_all('input')}

if __name__ == '__main__':
    print(login(sys.argv[1], sys.argv[2]).cookies)
# new_soup = BeautifulSoup(resp.text, 'html.parser')

# print(resp.cookies)
# print(resp.history)
# print(resp.url)

# print("Posting request...")
# print(new_resp.history)
# print(new_resp.history[0].headers)
# print(new_resp.request.headers)
# print(new_resp.status_code)
# print(new_soup.url)

# print(new_resp.request.body)
# # print(new_resp.request.data)
# # print(new_resp.data)

# # print(new_soup.prettify())
# print(new_soup.headers)
# print(soup.content)
# print(new_resp.raw)

# if r.status_code == 200:
#     with open('captcha.jpeg', 'wb') as f:
#         r.raw.decode_content = True
#         shutil.copyfileobj(r.raw, f)
# print(soup.findAll("img")[1]['src'])#.split('"'))
# print(resp.status_code)
# print(resp.headers)
# print(soup.prettify())
# url2 = tohttps(resp.request.url)

# resp2 = requests.get('http://electsys.sjtu.edu.cn/edu/login.aspx', headers = hd)
# print(BeautifulSoup(resp2.text, 'html.parser').prettify())
