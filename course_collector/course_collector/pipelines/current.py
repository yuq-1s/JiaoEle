# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem
from pdb import set_trace
from logging import getLogger
from course_collector.items import Course

logger = getLogger(__name__)

class CurrentPipeline(object):
    def process_item(self, item, spider):
        return item
