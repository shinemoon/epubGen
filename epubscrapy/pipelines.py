# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class EpubscrapyPipeline:
    def process_item(self, item, spider):
        spider.crawler.stats.inc_value('page_cnt')
        # For Index handling
        if(item['type']=='index'):
            print(item)
        return item


