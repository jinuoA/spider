# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class ExampleItem(Item):
    item_title = Field()
    task_id = Field()
    item_url = Field()
    dept_id = Field()
    item_pulishdate = Field()
    dept_name_key = Field()



