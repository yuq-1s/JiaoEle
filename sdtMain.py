#! /usr/bin/env python3

import requests
from bs4 import BeautifulSoup

def tohttps(oriurl):
    prot, body = edu_resp.request.url.split(':')
    return prot + 's' + body

def get_captcha_src(soup):
    for img_tag in soup.findAll('img'):
        if img_tag['src'].startswith('captcha?'):
            return img_tag['src']
    raise "Cannot find captcha."

hd = {  # 'Cookie': '''ASP.NET_SessionId=j2cywsrkdvyxin55534yo1i2;
        # mail_test_cookie=IJIBHIAK''',
        'Host': 'electsys.sjtu.edu.cn',
        # 'Upgrade-Insecure-Requests': 1,
        'Cookie':
        'ASP.NET_SessionId=j2cywsrkdvyxin55534yo1i2;JASiteCookie=CA4KehZCYxWVFyEAXjBRrZRBJujp0rJkec9L1bSM+9+Psk1aJ+amIxP5EUYaqlVVBP+tEubIulfUF8KnfLHv/jNsgmB5VmVW+EfcQBsnoxDf7Vmux3wqXFMZJmPdbJb0FdZJC+sORIyhKa47CX+Lz2VD8erMRRqgaiX5+8j1sLtnhWvP+yk0FMP0xawbN2/dNeGB8e6pXdqmanLIb4jL6rnYIRNZkh73MgLFu6LDaOOPKB2M8O4NWfUymduMAqkUrOud/cw+tC0oyABHWFG57XOZ2DRFpfq28J6RBlbn5d/xFKsVMQhh76KKFcGC4e7ErT3p3kej1qb2hZYDOrgVSclKBCrpKly4n3qulA1TjTm0gNNCmVqR2LVknCwAG2ZPLiK20xMUXqbM4ar7eWL+V44w7iZDOF/3FL/L4IJkZ8AdmNE8qFmbftI;mail_test_cookie=IJIBHIAK',
        'Accept': '''text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8''',
        }
edu_resp = requests.get('http://electsys.sjtu.edu.cn/edu/student/sdtMain.aspx', headers =
        hd)
edu_soup = BeautifulSoup(edu_resp.text, 'html.parser')
# print(edu_soup.findAll("div", { "class" : "captcha-input" }))
# print(edu_soup.findAll("img")[1])#.split('"'))
print(edu_soup.prettify())
# print(getcaptcha(edu_soup))
# print(edu_soup.findAll("img")[1]['src'])#.split('"'))

# print(edu_resp.status_code)
# print(edu_resp.headers)
# print(edu_soup.prettify())
# url2 = tohttps(edu_resp.request.url)

# resp2 = requests.get('http://electsys.sjtu.edu.cn/edu/login.aspx', headers = hd)
# print(BeautifulSoup(resp2.text, 'html.parser').prettify())
