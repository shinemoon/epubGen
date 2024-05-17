# Add Spider based solution:
from scrapy.crawler import CrawlerProcess
from epubscrapy.spiders.epubgen import EpubgenSpider
from scrapy.utils.project import get_project_settings


import fire
import os

def getBookIndex(bkUrl=""):
    """
    To Scan one book's index, to save it into json file, and return summary of result.

    Args:
        bkUrl (str):  Book's index page.

    Returns:
        Array: book list info.
    """
    import pdb

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
    process.crawl(EpubgenSpider, start_urls=[bkUrl])
    
    # Start the crawling process and add a callback to log stats after the crawl
    process.start(stop_after_crawl=True)
    #log_stats(process)

    blist = []
    return blist

# Function to log the stats after the crawl
# 似乎没必要，scrapy自己会打印
def log_stats(process):
    for crawler in process.crawlers:
        stats = crawler.stats.get_stats()
        logging.info('Crawl stats: %s', stats)

# Start/Resume to fetch content

if __name__=='__main__':
    fire.Fire(getBookIndex)
