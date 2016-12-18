#! /usr/bin/python3
# -*- coding: utf-8 -*-
# import jaccount, sdtMain

from pathlib import Path
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.utils.project import get_project_settings
from course_collector.spiders.current_courses import CurrentSpider
from course_collector.spiders.tongshi import TongShiSpider
from logging import getLogger
from twisted.internet import reactor
from pdb import set_trace

import copy
import time
import json
import os
import sys
import re
import cmd

logger = getLogger(__name__)

# class Course(object):
#     def __init__(self, course):
#         self.course = course
#         # self.odd = [{o['weekday']: course['odd_week']
#         # self.even = course['even_week']

#     def contains(self, other):
#         all(other.course

def are_overlap(course1, course2):
    def have_overlap(low1, high1, low2, high2):
        low1 = int(low1)
        high1 = int(high1)
        low2 = int(low2)
        high2 = int(high2)
        assert low1 <= high1 and low2 <= high2
        return not (low1 > high2 or low2 > high1)

    for parity in ('odd_week', 'even_week'):
        for c1 in course1.get(parity, {}):
            for c2 in course2.get(parity, {}):
                if c1['weekday'] == c2['weekday'] \
            and have_overlap(c1['wbegin'], c1['wend'], c2['wbegin'],c2['wend'])\
            and have_overlap(c1['cbegin'], c1['cend'], c2['cbegin'],c2['cend']):
                    return True
    return False

def contains(course1, course2):
    def period_contains(p1, p2):
        return p1['weekday'] == p2['weekday'] \
                and int(p1['wbegin']) <= int(p2['wbegin']) \
                and int(p1['wend']) >= int(p2['wend']) \
                and int(p1['cbegin']) <= int(p2['cbegin']) \
                and int(p1['cend']) >= int(p2['cend'])

    for parity in ('odd_week', 'even_week'):
        if not all(any(period_contains(p1, p2) for p1 in course1[parity]) \
                for p2 in course2[parity]):
            return False
    return True

    # def interval_contains(low1, high1, low2, high2):
    #     low1 = int(low1)
    #     high1 = int(high1)
    #     low2 = int(low2)
    #     high2 = int(high2)
    #     assert low1 <= high1 and low2 <= high2
    #     return low1 <= low2 and high1 >= high2

    # return all(c1['weekday'] == c2['weekday'] \
    #         and interval_contains(c1['wbegin'], c1['wend'], c2['wbegin'],c2['wend'])\
    #         and interval_contains(c1['cbegin'], c1['cend'], c2['cbegin'],c2['cend'])\
    #         for c1 in course1[parity] for c2 in course2[parity] \
    #         for parity in ('odd_week', 'even_week'))

    # for parity in ('odd_week', 'even_week'):
    #     for c1 in course1.get(parity, {}):
    #         for c2 in course2.get(parity, {}):
    #             if c1['weekday'] != c2['weekday'] \
    #                     or not interval_contains(c1['wbegin'], c1['wend'], c2['wbegin'],c2['wend'])\
    #                     or not interval_contains(c1['cbegin'], c1['cend'], c2['cbegin'],c2['cend']):
    #                         return False
    # return True


def get_feed_path(spider):
    return spider.custom_settings['FEED_URI'].split('file://')[1]

def load_file(filename):
        with open(filename, 'r') as f:
            return json.load(f)

# TODO: Make Spiders share the cookie middleware.
class Main(cmd.Cmd):
    CURRENT_PATH = get_feed_path(CurrentSpider) # Path(get_feed_path(CurrentSpider))
    COURSES_PATH = get_feed_path(TongShiSpider) # Path(get_feed_path(TongShiSpider))
    EXPIRE_SEC = 900
    prompt = '>> '
    def __init__(self, user = 'a', passwd = 'b'):
        super().__init__()
        process = CrawlerProcess(get_project_settings())
        need_restart = False

        # if not self.CURRENT_PATH.is_file() or \
        #         time.time()-self.CURRENT_PATH.stat().st_mtime>self.EXPIRE_SEC:
        #     # try:
        #     #     os.remove(self.CURRENT_PATH)
        #     # except FileNotFoundError:
        #     #     pass
        #     process.crawl(CurrentSpider)
        #     need_restart = True
        #     logger.info('Preparing to update selected courses...')
# #         if not self.COURSES_PATH.is_file():
# #             process.crawl(CurrentSpider)
# #             need_restart = True
# #             logger.info('Preparing to update available courses...')
        # if need_restart:
        #     logger.info('Updating...')
        #     process.start()
        #     os.execl(sys.executable, sys.executable, *sys.argv)

        self.current = load_file(self.CURRENT_PATH)
        self.courses = load_file(self.COURSES_PATH)
        # tmp = load_file(get_feed_path(TongShiSpider))
        # sunzi = copy.deepcopy(tmp[0])
        # last = tmp[0]
        # for i, c in enumerate(tmp[1:]):
        #     tmp[i-1]['name'] = c['name']
        # tmp[-1]['name'] = '工程可持续发展'
        # self.courses = [sunzi]+tmp
        # logger.info('Initialization succeeded.')

    @staticmethod
    def parse_query(raw):
        odd = []
        even = []
        for period in raw.split(';'):
            try:
                r=re.match('\'?\"?(\d)\s+(\d+)\s+(\d+)(?:\s+(\d+)\s+(\d+))?(\s+[oe]{1,2})?\'?\"?',period).groups()
                if len(r) != 6: continue
                if not any(r): continue
                queried_time = {}
                queried_time['wbegin'] = r[3] if r[3] else 1
                queried_time['wend'] = r[4] if r[4] else 16
                # ret['wbegin'] = r[5] if r[5] else 'oe'
                assert r[0] and 1 <= int(r[0]) <= 7, 'Weekday must in range 1-7'
                assert r[1] and 1 <= int(r[1]) <= 14, 'Course period must be in range 1-14'
                assert r[2] and 1 <= int(r[2]) <= 14, 'Course period must be in range 1-14'
                assert 1 <= int(queried_time['wbegin']) <= 16, 'Week period must in range 1-16'
                assert 1 <= int(queried_time['wend']) <= 16, 'Week peroid must in range 1-16'
                queried_time['cbegin'], queried_time['cend']=min(int(r[1]), int(r[2])), max(int(r[1]), int(r[2]))
                queried_time['weekday'] = '日一二三四五六'[int(r[0])]
                # queried_time['cbegin'] = int(r[1])
                # queried_time['cend'] = int(r[2])
                parity = r[5] if r[5] else 'oe'

                if 'o' in parity:
                    if queried_time not in odd:
                        odd.append(queried_time)
                if 'e' in parity:
                    if queried_time not in even:
                        even.append(queried_time)

            except AssertionError as e:
                logger.warn(e)
                logger.warn('Ignored: %s', period)
            except AttributeError as e:
                logger.warn(e)
                logger.warn('Ignored: %s', period)
                logger.warn('Invalid syntax')

        return {'odd_week': odd, 'even_week': even}

    def ls_all(self):
        for c in self.courses:
            print(c['name'])

    def get_all_non_overlap(self):
        return {c['name'] for c in self.courses for curr in self.current if not
                are_overlap(c, curr)}

        # for course in self.courses:
        #     for curr in self.current:
        #         if not are_overlap(course, curr):
        #             print(course['name'])

    def non_overlap_by_time(self, raw):
        ''' Usage: <2, 1, 3[, 1, 8][, 'o']>[;...]
            @return: Course names that do not overlap with any queried period,
                    without considering current selected courses.
        '''

        # TODO: add usage info
        queried = Main.parse_query(raw)
        if not queried['odd_week'] and not queried['even_week']:
            logger.warn('Invalid input, nothing to query.')
            # return set()
        return {c['name'] for c in self.courses if not are_overlap(c, queried)}

    def do_period(self, raw):
        ''' Return courses contained in your queries

            Example: >> period '2 9 10 o;4 7 8 1 8 e'
                    will show courses contained in the union of 
                    Tuesday from 9 to 10 节 from 1 to 16 odd weeks and 
                    Thursday from 7 to 8 节 from 1 to 8 even weeks.
        '''
        queried = Main.parse_query(raw)
        if not queried['odd_week'] and not queried['even_week']:
            logger.warn('Invalid input, nothing to query.')
            # print(set())

        print({c['name'] for c in self.courses if contains(queried, c)})

    def do_bye(self, arg):
        print('Bye')
        return True

# TODO: argparse
def main():
    process = CrawlerProcess(get_project_settings())
    print('Start')
    process.crawl('current')
    process.start()
    print('End')
    # course_info_file = Path('data/courses.json')
    current_courses = Path('/tmp/yuq_test_spider.json')
    with open('/tmp/yuq_test_spider.json', 'r') as f:
        courses = json.load(f)
    print(courses)
    # if not course_info_file.is_file():
    #     # TODO: Try to download the file from peers.
    #     print("Scraping target website.")

if __name__ == '__main__':
    # courses = load_file('data/courses1.json')
    # c1 = courses[0]
    # c2 = courses[1]
    # print(c1, c2)
    # print(contains(c1, c2))
    m1 = Main('a', 'b')

    m1.cmdloop()
    # print(m1.only_by_time('2 9 10 1 16 oe'))
    # print(m1.get_all_non_overlap())
