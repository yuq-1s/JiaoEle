# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Field, Item


# class CourseCollectorItem(scrapy.Item):
#     # define the fields for your item here like:
#     # name = scrapy.Field()
#     pass

class Course(Item):
    course_type = Field()
    cid = Field()
    name = Field()
    credit = Field()
    teacher = Field()
    duration = Field()
    max_member = Field()
    min_member = Field()
    week = Field()
    bsid = Field()
    remark = Field()

