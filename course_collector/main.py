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
import json
import os

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
    def __init__(self, user, passwd):
        process = CrawlerProcess()
        if not Path(get_feed_path(CurrentSpider)).is_file():
            process.crawl(CurrentSpider)
        if not Path(get_feed_path(TongShiSpider)).is_file():
            process.crawl(TongShiSpider, user, passwd)
        process.start()

        self.current = load_file(get_feed_path(CurrentSpider))
        self.courses = load_file(get_feed_path(TongShiSpider))

    def list_all(self):
        for c in self.current:
            print(c['name'])

        for c in self.courses:
            print(c['name'])

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
