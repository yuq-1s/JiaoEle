# -*- coding: utf-8 -*-
from scrapy import Item, Field
class Student(Item):
    name = Field() # 姓名
    xh = Field() # 学号
    xy = Field() # 学院
    zy = Field() # 专业

class Course(Item):
    bsid = Field()
    name = Field()
    cid = Field()
    credit = Field()
    hours = Field()
    kind = Field()
    time = Field() # '1-16;1;3-4' 'Odd;3:1-2'

