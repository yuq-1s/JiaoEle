#! /usr/bin/python3
# import jaccount, sdtMain
from pathlib import Path
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.utils.project import get_project_settings
from course_collector.spiders.current_courses import CurrentSpider
from course_collector.spiders.tongshi import TongShiSpider
from logging import getLogger
from twisted.internet import reactor
from pdb import set_trace
import time
import json
import os
import sys

logger = getLogger(__name__)

def are_overlap(course1, course2):
    def have_overlap(low1, high1, low2, high2):
        assert low1 <= high1 and low2 <= high2
        return not (low1 > high2 or low2 > high1)

    for parity in ('odd_week', 'even_week'):
        for c1 in course1[parity]:
            for c2 in course2[parity]:
                if c1['weekday'] == c2['weekday'] \
            and have_overlap(c1['wbegin'], c1['wend'], c2['wbegin'],c2['wend'])\
            and have_overlap(c1['cbegin'], c1['cend'], c2['cbegin'],c2['cend']):
                    return True
    return False

def get_feed_path(spider):
    return spider.custom_settings['FEED_URI'].split('file://')[1]

def load_file(filename):
        with open(filename, 'r') as f:
            return json.load(f)

# TODO: Make Spiders share the cookie middleware.
class Main(object):
    CURRENT_PATH = Path(get_feed_path(CurrentSpider))
    COURSES_PATH = Path(get_feed_path(TongShiSpider))
    EXPIRE_SEC = 900
    def __init__(self, user, passwd):
        process = CrawlerProcess(get_project_settings())
        need_restart = False

        if not CURRENT_PATH.is_file() or \
                time.time()-CURRENT_PATH.stat().st_mtime>EXPIRE_SEC:
            try:
                os.remove(CURRENT_PATH)
            except FileNotFoundError:
                pass
            process.crawl(TongShiSpider, user, passwd)
            need_restart = True
            logger.info('Preparing to update selected courses...')
        if not COURSES_PATH.is_file():
            process.crawl(CurrentSpider)
            need_restart = True
            logger.info('Preparing to update available courses...')
        if need_restart:
            logger.info('Updating...')
            process.start()
            os.execl(sys.executable, sys.executable, *sys.argv)

        self.current = load_file(get_feed_path(CurrentSpider))
        self.courses = load_file(get_feed_path(TongShiSpider))
        logger.info('Initialization succeeded.')

    def ls_all(self):
        for c in self.courses:
            print(c['name'])

    def get_all_non_overlap(self):
        return {c for c in self.courses for curr in self.current if not
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
        def parse_query(raw):
            queried = []
            for period in raw.split(';'):
                try:
                    r = re.match('(?:\s*(\d)\s+(\d+)\s+(\d+)\s*(?:(\d+)\s+(\d+)\s*)?([oe]?))')
                    if len(r) != 6: continue
                    if not any(r): continue
                    ret = {}
                    ret['wbegin'] = int(r[3]) if r[3] else 1
                    ret['wend'] = int(r[4]) if r[4] else 16
                    ret['wbegin'] = r[5] if r[5] else 'oe'
                    assert r[0] and 1 <= r[0] <= 7, 'Weekday must in range 1-7'
                    assert r[1] and 1 <= r[1] <= 14, 'Course period must be in range 1-14'
                    assert r[2] and 1 <= r[2] <= 14, 'Course period must be in range 1-14'
                    assert 1 <= ret['wbegin'] <= 16, 'Week period must in range 1-16'
                    assert 1 <= ret['wend'] <= 16, 'Week peroid must in range 1-16'
                    r[1], r[2] = min(r[1], r[2]), max(r[1], r[2])
                    ret['weekday'] = r[0]
                    ret['cbegin'] = r[1]
                    ret['cend'] = r[2]
                    queried.append(ret)
                except AssertionError as e:
                    logger.warn(e)
                    logger.warn('Ignored: %s', period)
            return queried

        # TODO: add usage info
        queried = parse_query(raw)
        if not queried:
            logger.warn('Invalid input, nothing to query.')
            return set()
        return {c['name'] for c in self.courses for q in queried if not
                are_overlap(c, q)}

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
    Main('a', 'b')
