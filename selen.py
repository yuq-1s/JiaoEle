#! /usr/bin/python3
# coding: utf-8

from selenium import webdriver
from pdb import set_trace
from jaccount import login
from time import sleep
from selenium.common.exceptions import NoSuchElementException
from functools import wraps
from urllib.parse import unquote

import sys
import traceback
import cmd
import logging
import requests
import re

# logging = getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(message)s', 
        datefmt='%m/%d/%Y %I:%M:%S %p',
        level=logging.INFO)

EDU_URL = 'http://electsys.sjtu.edu.cn/edu/'
ELECT_URL = EDU_URL+'student/elect/'

def prepare_cookie(sess):
    ele_cookies_list = ['ASP.NET_SessionId', 'mail_test_cookie']
    cookies = {s: sess.cookies[s] for s in ele_cookies_list}
    return [{'name': key, 'value': val, 'path': '/edu'} for key, val in cookies.items()]

class BasePage(object):
    def __init__(self, driver):
        self.driver = driver

    @classmethod
    def recover(cls, func):
        @wraps(func)
        def wrapper(self, *args, **kw):
            self.driver.get(self.recover_url)
            return func(self, *args, **kw)
        return wrapper

                # except NoSuchElementException:
                #     logging.warn('Not in CommonCourse page, nagivating to it...')
                #     self.driver.get(ELECT_URL+'speltyCommonCourse.aspx')

class InitPage(BasePage):
    recover_url = ELECT_URL+'electwarning.aspx?xklc=1'

    @BasePage.recover
    def init(self):
        self.driver.find_element_by_id('CheckBox1').click()
        self.driver.find_element_by_id('btnContinue').click()

class TongshiPage(BasePage):
    recover_url = ELECT_URL+'speltyCommonCourse.aspx'

    @BasePage.recover
    def get_courses_list(self, course_type):
        ct = ['rw', 'sk', 'zk', 'sx'].index(course_type)+2
        self.driver.find_element_by_xpath('//*[@id="gridGModule_ctl0%s_radioButton"]'%ct).click()
        assert 'speltyCommonCourse' in self.driver.current_url, 'get course list failed.'


    def get_name_by_cid(self, cid):
        return self.driver.find_element_by_xpath('//td[contains(text(),"%s")]/../td[1]'%cid).text

    def get_radio_by_cid(self, cid):
        return self.driver.find_element_by_xpath('//input[@value="%s"]'%cid)

    def view_lesson_by_cid(self, cid):
        self.get_radio_by_cid(cid).click()
        self.driver.find_element_by_id('lessonArrange').click()
        assert 'viewLessonArrange' in self.driver.current_url, 'view lesson failed'

    def submit(self):
        self.driver.find_element_by_id('btnSubmit').click()

class LessonPage(BasePage): 
    def get_teacher_by_bsid(self, bsid):
        return self.driver.find_element_by_xpath('//input[value="%s"]/../../../td[1]')

    def select_by_bsid(self, bsid):
        self.driver.find_element_by_xpath('//input[@value="%s"]'%bsid).click()
        self.driver.find_element_by_id('LessonTime1_btnChoose').click()
        # assert 'speltyCommonCourse' in self.driver.current_url, 'select failed.'

class MessagePage(BasePage):
    def back(self):
        self.driver.back()

    def handle_message(self):
        if 'message=' not in self.driver.current_url: return
        message = self.driver.current_url.split('message=')[1]
        logging.error(unquote(message))
        self.back()

class Main(cmd.Cmd):
    intro = '''Here is the evil software to grab courses of SJTU. Have fun ;)'''
    prompt = '>> '

    def preloop(self):
        self.user = 'zxdewr'# input('Enter username: ')
        self.passwd = 'ca1l6ack' #input('Enter password: ')

        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(1)
        self.driver.get(EDU_URL)
        self.update_cookies()

    def update_cookies(self):
        self.cookies = prepare_cookie(login(self.user, self.passwd))

        for c in self.cookies:
            self.driver.add_cookie(c)

    def do_qiang(self, arg):
        ''' Example: qiang rw TH901 382102
            for 抢人文课号为TH901, 老师代码为382102的
        '''

        while True:
            try:
                ct, cid, bsid = re.search('([a-z]{2})\s+([A-Z]{2}\d{3})\s+(\d{6})', arg).groups()
                initpage = InitPage(self.driver)
                tongshipage = TongshiPage(self.driver)
                lessonpage = LessonPage(self.driver)
                messagepage = MessagePage(self.driver)

                initpage.init()
                tongshipage.get_courses_list(ct)
                while True:
                    try:
                        tongshipage.view_lesson_by_cid(cid)
                        lessonpage.select_by_bsid(bsid)
                        messagepage.back()
                    except NoSuchElementException:
                        sleep(1)
                        tongshipage.submit()
                        self.driver.get(EDU_URL+'login.aspx')

                return
            except AssertionError as e:
                traceback.print_exc(file=sys.stdout)
                logging.error(e)
                continue

            except Exception as e:
                if 'jaccount' in self.driver.current_url:
                    self.update_cookies()
                    continue
                if 'commitConflict.aspx' in self.driver.current_url:
                    self.driver.back()
                    continue
                if 'outTimePage.aspx' in self.driver.current_url:
                    self.driver.get(EDU_URL+'login.aspx')
                    continue
                if 'message=' in self.driver.current_url:
                    messagepage.handle_message()
                    continue

                traceback.print_exc(file=sys.stdout)
                logging.error(e)
                return 

    def do_quit(self, arg):
        print('Bye')
        return True

        # ret = {}
        # while True:
        #     try:
        #         ret['cid'] = input('Course number: ')
        #         ret['bsid'] = input('bsid: ')

        #         print('Ready to get {course_type},{cid},{bsid}'.format(ret))
        #         if input('Confirm? [y]/n') == 'y': return ret
        #     except ValueError as e:
        #        if str(e) == 'q' or str(e) == 'quit': return None

#         def parse_type(course_type):
#             ''' 请输入通识课拼音首字母
#                 人文: rw
#                 社科: sk
#                 自科: zk
#                 数学: sx
#                 退出: q
#             '''
#             while True:
#                 valid_input = ['rw','sk','zk','sx']
#                 try:
#                     return '//*[@id="gridGModule_ctl0%s_radioButton"]'%(valid_input.index(course_type)+2)
#                 except ValueError as e:
#                     if str(e) == 'q' or str(e) == 'quit': return None
#                     print('%s not found.\n'%str(e) + __doc__)

#         def parse_number(number):
#             return '//input[@value="%s"]'%number

#         def 
#         self.driver.find_element_by_xpath('//input[@value="%s"]'k)

#     def do_grab(self):
        
def main():
    def audition(driver):
        while True:
            try:
                # driver.get(EDU_URL+'student/sdtleft.aspx')
                # driver.find_element_by_link_text('一专选课').click()
                # while True:
                #     try:
                #         driver.find_element_by_link_text('海选').click()
                #     except NoSuchElementException:
                #         break
                while True:
                    driver.get('http://electsys.sjtu.edu.cn/edu/student/elect/electwarning.aspx?xklc=1')
                    driver.find_element_by_id('CheckBox1').click()
                    driver.find_element_by_id('btnContinue').click()

                    while 'Common' not in driver.current_url:
                        try:
                            # 通识课
                            driver.find_element_by_id('SpeltyRequiredCourse1_btnTxk').click()
                        except NoSuchElementException as e:
                            logging.info('Cannot find element %s' %str(e))
                            pass

                    if driver.find_element_by_id('ScoreInfo1_lblTargetS').text!='0':
                        return driver
            except NoSuchElementException:
                logging.info('Cannot find element %s' %str(e))
                pass

    driver = init('zxdewr', 'ca1l6ack')
    driver = audition(driver)

    while True:
        try:
            # 人文
            driver.find_element_by_xpath(get_course_type_xpath()).click()
            # 爱的艺术与人生
            driver.find_element_by_css_selector('#gridMain_ctl34_Label2 > input[type="radio"]').click()
            # 课程安排
            driver.find_element_by_id('lessonArrange').click()
            # 陈玲玲
            driver.find_element_by_css_selector('#LessonTime1_gridMain_ctl03_Label2 > input[type="radio"]').click()
            try:
                while True:
                    # 选定此教师
                    driver.find_element_by_id('LessonTime1_btnChoose').click()
                    # 返回
                    driver.back()
                    # driver.find_element_by_id('LessonTime1_Button1').click()
                    # sleep(1)
            except NoSuchElementException:
                # 选课提交
                driver.find_element_by_id('btnSubmit').click()
                print(driver.find_element_by_id('lblMessage').text)
        # # None is passed, the user canceled.
        # except TypeError:
        #     pass

        except NoSuchElementException as e:
            if 'message=' in driver.current_url:
                logging.error(driver.current_url.split('message=')[1])
                driver.back()
            logging.info(str(e))
            driver = audition(driver())

if __name__ == '__main__':
    Main().cmdloop()
    # main()


    # driver = webdriver.Chrome()
    # driver.get('http://electsys.sjtu.edu.cn')

    # # for cookie in cookies:
    # #     driver.add_cookie(cookie)

    # # driver.get('http://electsys.sjtu.edu.cn')
    # # for cookie in cookies:
    # #     driver.add_cookie(cookie)
    # driver.get('http://electsys.sjtu.edu.cn/edu/student/elect/speltyCommonCourse.aspx')
    # # 人文
    # driver.find_element_by_xpath('//*[@id="gridGModule_ctl02_radioButton"]').click()
    # sleep(1)
    # # 爱的艺术与人生
    # driver.find_element_by_css_selector('#gridMain_ctl34_Label2 > input[type="radio"]').click()
    # sleep(1)
    # # 课程安排
    # driver.find_element_by_id('lessonArrange').click()
    # sleep(1)
    # # 陈玲玲
    # driver.find_element_by_css_selector('#LessonTime1_gridMain_ctl02_Label2 > input[type="radio"]').click()
    # sleep(1)
    # try:
    #     while True:
    #         # 选定此教师
    #         driver.find_element_by_id('LessonTime1_btnChoose').click()
    #         sleep(1)
    #         # 返回
    #         driver.find_element_by_id('LessonTime1_Button1').click()
    #         sleep(1)
    # except NoSuchElementException:
    #     # 选课提交
    #     driver.find_element_by_id('btnSubmit').click()
    #     sleep(1)

    # # while True:
    # #     driver.get('http://electsys.sjtu.edu.cn/edu/login.aspx')
    # #     user = driver.find_element_by_id('user')
    # #     passwd = driver.find_element_by_id('pass')
    # #     capt = driver.find_element_by_id('captcha')
    # #     user.send_keys('zxdewr')
    # #     passwd.send_keys('ca1l6ack')
    # #     img_url=driver.find_element_by_xpath('//*[@id="login-form"]/form/div[3]/img').get_attribute('src')
    # #     captcha =image_to_string(Image.open(BytesIO(requests.get(img_url).content)))
    # #     capt.send_keys(captcha)
    # #     set_trace()
    # #     resp = driver.find_element_by_css_selector('#login-form > form > div:nth-child(8) > input').click()
    # #     if 'message=' not in resp.url: break
    # #     print(driver.get_cookies())

    # set_trace()
