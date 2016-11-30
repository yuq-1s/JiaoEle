#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from jaccount import login
from bs4 import BeautifulSoup as bs
from sdtMain import asp_params
import requests

ELECT_URL = 'http://electsys.sjtu.edu.cn/edu/student/elect/'

if __name__ == '__main__':
    for cnt in range(5):
        sess = login('zxdewr', 'pypy11u')
        print(asp_params(sess.get(ELECT_URL+'electwarning.aspx').text))



