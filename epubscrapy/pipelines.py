# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json


class EpubscrapyPipeline:
    def process_item(self, item, spider):
        spider.crawler.stats.inc_value('page_cnt')
        # For Index handling
        if(item['type']=='index'):
            wId = item['wId']
            file_path = r'working/'+wId+'/workingList'
            #插入到任务列表
            # 读取现有的字典列表
            try:
                with open(file_path, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
            except FileNotFoundError:
                data = []
    
            # 将新的 item 插入到列表中
            data.append(dict(item))
    
            # 将更新后的列表写回文件
            with open(file_path, 'w', encoding='utf-8') as fp:
                json.dump(data, fp, ensure_ascii=False, indent=4)
        return item
