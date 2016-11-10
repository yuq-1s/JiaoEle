#! /usr/bin/env python3

import requests
import shutil
import urllib as ul
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
    cap_src = captcha_src(soup)
    r = sess.get('https://jaccount.sjtu.edu.cn/jaccount/'+cap_src, stream=True)
    img = Image.open(BytesIO(r.content))
    img.show()
    return input('What\'s in the image?\n')

def post_data(sess, soup):
    form = ['sid', 'returl', 'se', 'v']

    data = dict(zip(form, [soup.find('input', {'name': s}).get('value') for s in form]))
    data['user'] = 'username'
    data['pass'] = 'password'
    data['captcha'] = input_captcha(sess, soup)
    return data

def login(user, password):
    sess = requests.Session()
    resp = sess.get('http://electsys.sjtu.edu.cn/edu/login.aspx')
    soup = BeautifulSoup(resp.text, 'html.parser')
    post_url = 'https://jaccount.sjtu.edu.cn/jaccount/ulogin'

    resp = sess.post(post_url, data = post_data(sess, soup))
    return sess

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
