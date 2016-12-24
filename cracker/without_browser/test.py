#! /usr/bin/env python3
# -*- coding: utf-8 -*-

class Test(object):

    def __init__(self):
        self.user = 'zxdewr'
        self.passwd = 'ca1l6ack'
        self.sess = login(self.user, self.passwd)

        url = ELECT_URL+'electwarning.aspx?xklc=1'
        init_param = {'CheckBox1': 'on', 'btnContinue': '继续'}
        init_param.update(asp_params(self.sess.get(url).text))

        param = {'SpeltyRequiredCourse1$btnQxsy': '抢选首页'}
        param.update(asp_params(self.sess.post(url, data=init_param).text))
        url = ELECT_URL+'speltyRequiredCourse.aspx'

        self.qxresp = self.sess.post(url=url, data=param)
        self.bsids = re.findall('bsid=(\d{6})', self.qxresp.text)
        self.params = [{'__EVENTTARGET': tag.parent.parent.a.attrs['href'].split("'")[1]} 
                for tag in BeautifulSoup(self.qxresp.text,'html.parser').find_all('font', {'color': 'Red'}) \
                        if tag.parent.parent.a and tag.text == '否']

    def doit(self):
        def get_bsid(text):
            soup = BeautifulSoup(text, 'html.parser')
            for inp in soup.find_all('input', {'type': 'radio'}):
                if inp['value'] in self.bsids:
                    return inp['value']

        url = ELECT_URL+'secondRoundFP.aspx'
        for param in self.params:
            param.update(asp_params(self.qxresp.text))

            lesson_resp = self.sess.post(url=url, data=param)
            bsid = get_bsid(lesson_resp.text)
            if not bsid: continue


            submit_param = {'btnSubmit': '选课提交'}
            submit_param.update(asp_params(self.qxresp.text))
            while True:
                lesson_param = {'myradiogroup': bsid,
                        'LessonTime1$btnChoose': '选定此教师'}
                lesson_param.update(asp_params(lesson_resp.text))
                resp = self.sess.post(url=lesson_resp.url, data=lesson_param)
                if 'outTime' in resp.url:
                    self.sess = login(self.user, self.passwd)
                try:
                    message = resp.url.split('message=')[1]
                    if '刷新' in message:   sleep(1)
                    print(message)
                except IndexError:
                    try:
                        assert '/secondRoundFP.aspx' in resp.url
                        self.sess.post(self.qxresp.url, data=submit_param)
                    except AssertionError:
                        pass


def qiangxuanshouye(sess):
    # class Course(object):
    #     def __init__(self, soup):
    #         for tag in soup.find_all('font', {'color': 'Red'}):
    #             self.param = {'__EVENTTARGET': tag.parent.parent.a.attrs['href'].split("'")[1]}
    #             self.name = tag.parent.parent.a.string.strip()
    #             self.

    url='http://electsys.sjtu.edu.cn/edu/student/elect/secondRoundFP.aspx'
    query='?yxdm=&nj=2015&kcmk=-1&txkmk=-1&tskmk='

        # self.bsids = self.qxsoup.find_all('a', {'href': re.compile('bsid=\d+')})
        # soup = BeautifulSoup(sess.get(url).text, 'html.parser')

    view = asp_post(sess, url=url+query, recover_url=url,
            params={'__EVENTTARGET':'gridMain$ctl04$LinkButton1'})

    params = {'myradiogroup': '381716', 'LessonTime1$btnChoose': '选定此教师'}
    params.update(asp_params(view.text))
    # params = asp_params(resp1.text).update(p1)
    resp2 = sess.post(view.url, data=params)
    print(resp2)
    set_trace()

