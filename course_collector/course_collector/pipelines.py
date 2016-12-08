# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem
from pdb import set_trace
from logging import getLogger

logger = getLogger(__name__)

class CourseCollectorPipeline(object):
    def __init__(self):
        self.bsid_seen = set()

    def process_item(self, item, spider):
        logger.info(item['week'])
        if item['bsid'][0] in self.bsid_seen:
            raise DropItem("Duplicate item found: %s"%item)
        else:
            self.bsid_seen.add(item['bsid'][0])
            return item
