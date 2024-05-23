# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class EpubscrapyItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    content = scrapy.Field()
    url = scrapy.Field()
    type = scrapy.Field()
    wId = scrapy.Field()
    fId = scrapy.Field()
