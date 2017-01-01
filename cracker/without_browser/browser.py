from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from functools import wraps

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
    recover_url = ELECT_URL+'electwarning.aspx?xklc=2'

    @BasePage.recover
    def init(self):
        self.driver.find_element_by_id('CheckBox1').click()
        self.driver.find_element_by_id('btnContinue').click()
        # assert 'secondRoundFP.aspx' in self.driver.current_url, 'init failed'
        # # assert 'speltyR' in self.driver.current_url, 'init failed'

class TongshiPage(BasePage):
    recover_url = ELECT_URL+'speltyCommonCourse.aspx'
    def __init__(self, driver, course_type, cid):
        self.course_type = course_type
        self.cid = cid
        super().__init__(driver)

    @BasePage.recover
    def get_courses_list(self):
        ct = ['rw', 'sk', 'zk', 'sx'].index(self.course_type)+2
        self.driver.find_element_by_xpath('//*[@id="gridGModule_ctl0%s_radioButton"]'%ct).click()
        # assert '/speltyCommonCourse' in self.driver.current_url, 'get course list failed.'


    def get_name_by_cid(self):
        return self.driver.find_element_by_xpath('//td[contains(text(),"%s")]/../td[1]'%self.cid).text

    def get_radio_by_cid(self):
        return self.driver.find_element_by_xpath('//input[@value="%s"]'%self.cid)

    def view_lesson_by_cid(self):
        self.get_radio_by_cid().click()
        self.driver.find_element_by_id('lessonArrange').click()
        # assert '/viewLessonArrange' in self.driver.current_url, 'view lesson failed'

    def submit(self):
        self.driver.find_element_by_id('btnSubmit').click()

class LessonPage(BasePage): 
    def __init__(self, driver, bsid):
        self.bsid = bsid
        super().__init__(driver)

    def get_teacher_by_bsid(self):
        return self.driver.find_element_by_xpath('//input[value="%s"]/../../../td[1]')

    def select_by_bsid(self):
        self.driver.find_element_by_xpath('//input[@value="%s"]'%self.bsid).click()
        self.driver.find_element_by_id('LessonTime1_btnChoose').click()
        # assert 'speltyCommonCourse' in self.driver.current_url, 'select failed.'

class QiangxuanPage(BasePage):
    def proceed(self):
        self.driver.find_element_by_id('btnTxk').click()

class MessagePage(BasePage):
    def back(self):
        self.driver.back()
        # try:
        #     self.driver.find_element_by_id('btnContinue').click()
        # except NoSuchElementException:
        #     self.driver.find_element_by_id('Button1').click()

        # self.driver.back()

    def handle_message(self):
        # if 'message=' not in self.driver.current_url: return
        message = unquote(self.driver.current_url.split('message=')[1])
        if '刷新' in message: 
            sleep(1)
        logging.error(message)
        self.back()

class Qianger(object):
    def proceed(self):
        try:
            if '/viewLessonArrange' in self.driver.current_url:
                self.lessonpage.select_by_bsid()
                if not 'message=' in self.driver.current_url:
                    sleep(1.5)
                    self.tongshipage.submit()
                    logger.info('Succeeded.')
            elif '/speltyCommonCourse' in self.driver.current_url:
                sleep(1)
                self.tongshipage.get_courses_list()
                sleep(1)
                self.tongshipage.view_lesson_by_cid()
                sleep(1)
            elif 'message=' in self.driver.current_url:
                self.messagepage.handle_message()
            elif '/secondRoundFP.aspx' in self.driver.current_url:
                sleep(2)
                self.qxpage.proceed()
            else:
                self.initpage.init()
                sleep(1)

        except NoSuchElementException:
            pass
            # set_trace()
        except StaleElementReferenceException:
            pass


    def do_do_qiang(self, arg):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(1)
        self.driver.get(EDU_URL)
        self.update_cookies()

        try:
            ct, cid, bsid = re.search('([a-z]{2})\s+([A-Z]{2}\d{3})\s+(\d{6})', arg).groups()
            self.initpage = InitPage(self.driver)
            self.tongshipage = TongshiPage(self.driver, ct, cid)
            self.lessonpage = LessonPage(self.driver, bsid)
            self.messagepage = MessagePage(self.driver)
            self.qxpage = QiangxuanPage(self.driver)
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            logging.error(e)
            return

        while True:
            try:
                self.proceed()
                # initpage.init()
                # tongshipage.get_courses_list(ct)
                # # sleep(1)
                # while True:
                #     try:
                #         tongshipage.view_lesson_by_cid(cid)
                #         lessonpage.select_by_bsid(bsid)
                #         messagepage.handle_message()
                #     except (NoSuchElementException, IndexError):
                #         assert '/speltyCommonCourse' in self.driver.current_url
                #         sleep(1)
                #         tongshipage.submit()
                #         set_trace()
                #         # self.driver.get(EDU_URL+'login.aspx')
                #         logging.info('Success')
                #         return

            except AssertionError as e:
                traceback.print_exc(file=sys.stdout)
                if 'message=' in self.driver.current_url:
                    messagepage.handle_message()
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

    def update_cookies(self):
        cookie =prepare_cookie(login(self.user, self.passwd))
        print(cookie)
        self.cookies = prepare_cookie(login(self.user, self.passwd))

        for c in self.cookies:
            self.driver.add_cookie(c)

    def do_qiang(self, arg):
        ''' Example: qiang rw TH901 382102
            for 抢人文课号为TH901, 老师代码为382102的
        '''
        self.do_do_qiang(arg)
        # with ThreadPoolExecutor(max_workers=2) as executor:
        #     print(executor.submit(self.do_do_qiang, arg).result)
