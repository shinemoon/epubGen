# Add Spider based solution:
from scrapy.crawler import CrawlerProcess
from epubscrapy.spiders.epubgen import EpubgenSpider
from scrapy.utils.project import get_project_settings
from multiprocessing import Process

import subprocess, os, glob


import fire
import os
import pdb


curCfg= {
        #Site Info
        "name":"快书网",
        "url":"https://www.kuaishu5.com",
        "domain":["kuaishu5.com"],
        "defaultUrl":["https://www.kuaishu5.com/b252247/"],
        "cookies":{'t':'64d056276329451626481e87d09e8340','r':'4079'},
        "useplaywright":True,
        #Index Parser
        "pageKey":".index-container-btn",
        "indexKey":"#list #content_1 a",
        "indexHrefKey":"::attr(href)",
        "indexTitleKey":"dd::text",
        #Content Parser
        "contentKey":"#booktxt",
        "bookName":"#info h1::text",
        "authorName":"#info p:nth-child(2) a::text",
        "titleKey":"h1.bookname::text",
        "fetchDelay":2,
        "fmimg":"#fmimg img::attr(src)",
        "fmtype":"refine",
        #        "excludeKeys":["script","#content_tip","p"],
        "excludeKeys":["script"],
        #Mail
        "recmail":"shinemoon@foxmail.com",
        }


def runCrawl(bkUrl="", mode='index'):
    """
    To Scan one book's index, to save it into json file, and return summary of result.

    Args:
        bkUrl (str):  Book's index page.

    Returns:
        Array: book list info.
    """
    if bkUrl=="":
        bkUrl = "https://www.kuaishu5.com/b265521/"

    # 设置 scrapy.cfg 文件路径
    # 设置 Scrapy 项目的配置文件路径
    scrapy_cfg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'scrapy.cfg'))
    os.environ['SCRAPY_CFG'] = scrapy_cfg_path
    # 此处针对原本目录，需要调整目录层次
    os.environ['SCRAPY_SETTINGS_MODULE'] = 'epubscrapy.settings'
    # 获取 Scrapy 项目设置
    settings = get_project_settings()
    # Create a CrawlerProcess with the project settings
    process = CrawlerProcess(settings)
   

    # Add your spider to the process
    # 获取目录列表
    process.crawl(EpubgenSpider, start_urls=[bkUrl], conf=curCfg, mode=mode)
    process.start(stop_after_crawl=True)
    print(f"{mode} MODE DONE")

def run_spider_in_process(bkUrl, mode):
    p = Process(target=runCrawl, args=(bkUrl, mode))
    p.start()
    p.join()

def main(startUrl='', mode='all'):
    """书籍抓取生成工具

    用于生成书籍的工具脚本

    Usage: 
        startUrl : str
            对应书籍的目录页
        mode : str  
            任务类型
            - index: 生成目录列表
            - content: 抓取章节内容
            - gen: 生成电子书
            - all: 一键生成 

    Args:
        startUrl: 对应书籍的目录页
        mode: 任务模式

    """
    WMODE={'all':[1,1,1], 'index':[1,0,0], 'content':[0,1,0], 'gen':[0,0,1]}
    wow = WMODE[mode]

    #Start of Code
    if(wow[0]):
        run_spider_in_process(startUrl,'index')

    if(wow[1]):
        run_spider_in_process(startUrl,'content')



# Function to log the stats after the crawl
# 似乎没必要，scrapy自己会打印
def log_stats(process):
    for crawler in process.crawlers:
        stats = crawler.stats.get_stats()
        logging.info('Crawl stats: %s', stats)

# Start/Resume to fetch content

if __name__=='__main__':
    fire.Fire(main)
