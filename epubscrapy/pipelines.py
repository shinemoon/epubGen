# Define your item pipelines hresponse.css(self.cfg['
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from termcolor import colored, cprint

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json


class EpubscrapyPipeline:
    def process_item(self, item, spider):
        spider.crawler.stats.inc_value('page_cnt')
        wId = item['wId']
        # For Index handling
        if(item['type']=='index'):
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
        if(item['type']=='content'):
            fId = item['fId']
            cprint(f"{fId}: {item['url']}",'yellow',attrs=['dark'])
            # Delete backlog list item accordingly
            # 确保 wId 和 fId 是字符串
            wId = str(wId)
            fId = str(fId)
            # 构建文件路径
            file_path = 'working/'+wId+'/dumps/'+fId+'.json'
            print(file_path)
            with open(file_path, 'w') as fp:
                json.dump(dict(item),fp,ensure_ascii = False, indent=4)
                fp.flush()
        return 0

        return item
