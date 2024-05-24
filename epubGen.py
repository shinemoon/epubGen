# Add Spider based solution:
from scrapy.crawler import CrawlerProcess
from epubscrapy.spiders.epubgen import EpubgenSpider
from scrapy.utils.project import get_project_settings
from multiprocessing import Process
import subprocess, os, glob
import hashlib, subprocess
from utils import select_and_read_config
from termcolor import colored, cprint
import fire
import os
import pdb


from genepub import genEpubfromHtml


def runCrawl(bkUrl="", mode='index', cfg=None):
    """
    To Scan one book's index, to save it into json file, and return summary of result.

    Args:
        bkUrl (str):  Book's index page.

    Returns:
        Array: book list info.
    """

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
    process.crawl(EpubgenSpider, start_urls=[bkUrl], conf=cfg, mode=mode)
    process.start(stop_after_crawl=True)
    print(f"{mode} MODE DONE")

def run_spider_in_process(bkUrl, mode, cfg):
    p = Process(target=runCrawl, args=(bkUrl, mode, cfg))
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
    
    # 读取配置文件
    configs_dir = './configs'
    curCfg = select_and_read_config(configs_dir)
    #print(f"选定的文件内容: {selected_data}")

    startUrl  = str(input("请输入书籍目录页: "))

    if(startUrl==''):
        startUrl = "https://www.kuaishu5.com/b265521/"
    wId = hashlib.sha1(startUrl.encode("UTF-8")).hexdigest()[:10]

    WMODE={'all':[1,1,1,0], 'index':[1,0,0,0], 'content':[0,1,0,0], 'gen':[0,0,1,0], 'clean':[0,0,0,1]}
    wow = WMODE[mode]

    #Start of Code
    if(wow[0]):
        cprint(f"抓取索引目录","blue")
        run_spider_in_process(startUrl,'index', curCfg)

    if(wow[1]):
        cprint(f"抓取正文","blue")
        run_spider_in_process(startUrl,'content', curCfg)


    if(wow[2]):
        cprint(f"生成书籍","yellow")
        if(genEpubfromHtml('working/'+wId, curCfg, {'toc':True,'mail':False})==0):
            pass
            # to check if mail needed:
            #if(args.mail):
#                cprint("生成完毕，发送邮件!",'green',attrs=['bold'])
#                # Reconstruct the sendmail bash
#                mailcmd = "./send-mail.sh %s %s %s"%(siteConfigs['recmail'],'working/'+wId+'/'+binfo['name']+'.epub',binfo['name'])
#                # excute the sendmail cmd
#                cprint(mailcmd,'green',attrs=['dark'])
#                subprocess.run(mailcmd,shell=True, check=True)
#            else:
#                cprint("生成完毕！",'green',attrs=['bold'])

    if(wow[3]):
        #subprocess.run("rm -rf working/%s"%(wId),shell=True, check=True)
        subprocess.run("rm -rf working/*",shell=True, check=True)
        cprint(f"清理工作目录","red")



# Function to log the stats after the crawl
# 似乎没必要，scrapy自己会打印
def log_stats(process):
    for crawler in process.crawlers:
        stats = crawler.stats.get_stats()
        logging.info('Crawl stats: %s', stats)

# Start/Resume to fetch content

if __name__=='__main__':
    fire.Fire(main)
