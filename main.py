#! /usr/bin/python3
# import jaccount, sdtMain
# from course_collector.course_collector.spiders.tongshi import TongshiSpider
# from course_collector.course_collector.spiders.tongshi import SelectSpider
from pathlib import Path

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

# TODO: argparse
def main():
    course_info_file = Path('data/courses.json')
    if not course_info_file.is_file():
        # TODO: Try to download the file from peers.
        print("Scraping target website.")


