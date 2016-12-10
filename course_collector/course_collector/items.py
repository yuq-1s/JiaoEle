# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.loader.processors import MapCompose
from scrapy import Field, Item


# class CourseCollectorItem(scrapy.Item):
#     # define the fields for your item here like:
#     # name = scrapy.Field()
#     pass

class CourseTime(Item):
    weekday = Field()
    cbegin = Field()
    cend = Field()
    wbegin = Field()
    wend = Field()

class Course(Item):
    course_type = Field()
    cid = Field(input_processor=MapCompose(str.strip))
    name = Field(input_processor=MapCompose(str.strip))
    credit = Field()
    teacher = Field()
    # duration = Field()
    max_member = Field()
    min_member = Field()
    odd_week = Field()# serializer=CourseTime)
    even_week = Field()# serializer=CourseTime)
    # week = Field()
    bsid = Field()
    remark = Field(input_processor=MapCompose(str.strip))
    place = Field()
    # time = Field()

# class MetaItem(Item):
#     weekday = Field()
#     hour = Field()
#     place = Field()
#     week = Field()
#     teacher = Field()

# class MetaItemloader(ItemLoader)
#     define_item_class = MetaItem
#     def default_input_processor
#     def __weekday_parse(info_lst):
#         def __do_parse(info_str):
#             weekday = re.findall(r'星期(\w)', info_str)
#             hour = re.findall(r'第(\d+)节--第(\d+)节', info_str)
#             week = re.findall(r'\((\d+)-(\d+)周\)', info_str)
#             ':'.join(week)+':'+weekday+':'+':'.join(hour).
#             return {'weekday': re.findall(r'星期(\w)', info_str),
#                     'hour': re.findall(r'第(\d+)节--第(\d+)节', info_str),
#                     'place': re.findall(r'\s(\w+\d+)\(', info_str), # 下院100
#                     'week': re.findall(r'\((\d+)-(\d+)周\)', info_str),
#                     'teacher': re.findall(r'\.(\w+)\s(\w+)',info_str)# 教师 职称
#                     }

#         try:
#             odd = info_lst[info_lst.index('单周')+1:info_lst.index('双周')]
#             even = info_lst[info_lst.index('双周')+1:]
#             return [__do_parse(''.join(lines)) for lines in [odd, even]]
#         except ValueError:
#             return [__do_parse(''.join(info_lst))] * 2


