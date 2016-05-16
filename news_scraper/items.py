# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SoyaItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    date = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    contents = scrapy.Field()
    categories = scrapy.Field()
    tags = scrapy.Field()
    # comments = scrapy.Field()

class PaulTanItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    date = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    contents = scrapy.Field()
    categories = scrapy.Field()
    comments = scrapy.Field()
    
class CommentItem(scrapy.Item):
	author = scrapy.Field()
	contents = scrapy.Field()
	date = scrapy.Field()

class FoxItem(scrapy.Item):
    date = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    contents = scrapy.Field()
    # categories = scrapy.Field()
    # comments = scrapy.Field()

class BlogItem(scrapy.Item):
    author = scrapy.Field()
    title = scrapy.Field()
    contents = scrapy.Field()
    date = scrapy.Field()
    url = scrapy.Field()

class KissmetricBlogItem(scrapy.Item):
    author = scrapy.Field()
    title = scrapy.Field()
    contents = scrapy.Field()
    url = scrapy.Field()
