#! /usr/bin/python3
import jaccount, stdMain
from course_collector.course_collector.spider.tongshi import TongshiSpider
from course_collector.course_collector.spider.tongshi import SelectSpider
from pathlib import Path

# TODO: argparse
def main():
    course_info_file = Path('data/courses.json')
    if not course_info_file.is_file():
        # TODO: Try to download the file from peers.
        print("Scraping target website.")


