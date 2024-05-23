USEPLAYWRIGHT = True
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import pdb

import hashlib, subprocess, requests, json
from termcolor import colored, cprint
from utils import detectRealUrl,read_working_list
from url_normalize import url_normalize

from epubscrapy.items import EpubscrapyItem as chapter

class EpubgenSpider(CrawlSpider):
    name="epubGenSpider"
    cfg={}
    cookie_dict={}
    mode='index'
    wIdList=[]

    page = None

    custom_headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0'
    }
    custom_meta = {
            "playwright": USEPLAYWRIGHT,
            "playwright_include_page": USEPLAYWRIGHT,
            "cookiejar": 1,
            }

    # Set the log level to INFO for this specific spider
    common_settings = {
            "LOG_LEVEL": "ERROR",
            "LOG_FILE_APPEND": False,
            "ITEM_PIPELINES" : {
                'epubscrapy.pipelines.EpubscrapyPipeline': 300,
                },
            "DEFAULT_REQUEST_HEADERS": custom_headers,
    }
    if(USEPLAYWRIGHT):
        playwright_settings = {
                # For playWright Solution
                "DOWNLOAD_HANDLERS" : {
                    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
                    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
                    },
                "PLAYWRIGHT_LAUNCH_OPTIONS":{
                    "headless": True,
                    }
                }
    else:
        playwright_settings = {
                "DOWNLOADER_MIDDLEWARES" : {
                    'scrapy_playwright.middlewares.PlaywrightRequestMiddleware': None,
                    'scrapy_playwright.middlewares.PlaywrightResponseMiddleware': None,
                    }
                }
    custom_settings = {**common_settings, **playwright_settings}

    def initwConf(self, cfg, mode):
        self.mode=mode
        self.cfg=cfg
        self.allowed_domains = cfg["domain"]
        self.handle_httpstatus_list = [404,500, 403]
        #Default URL for Demo Purpose
        self.start_urls = cfg["defaultUrl"]
        if(mode=='index'):
            self.rules = [
                    # To fetch index list
                    Rule(LinkExtractor(allow=(), unique=True,restrict_css=cfg["pageKey"]), process_request='epubRequest',callback='parse_index', follow=True),
                    ]
        elif (mode=='content'):
            #书籍内容抓取
            #按照wId来获取工作文件列表
            self.rules = [
                    # Empty Rule, just following the start_urls from workinglist
                    ]
        self.cookie_dict = cfg["cookies"]
    
    def __init__(self, start_urls=None, conf=None, mode='index', *args, **kwargs):
        super(EpubgenSpider, self).__init__(*args, **kwargs)
        if conf is not None:
            self.initwConf(conf, mode=mode)
        # To Override Start Url
        if start_urls is not None:
            if(mode=='index'):
                self.start_urls = start_urls
            elif(mode=='content'):
                # To parse and get content list
                self.start_urls = []
                for url in start_urls:
                    wId = hashlib.sha1(url.encode("UTF-8")).hexdigest()[:10];
                    data = read_working_list(wId)
                    # 提取所有的url
                    self.start_urls = self.start_urls + [item['url'] for item in data]
                    self.wIdList = self.wIdList + [wId]*len(data)


    def parse(self, response):
        pass

    async def parse_index(self, response):
        if USEPLAYWRIGHT: 
            self.page = response.meta["playwright_page"]
        cprint(f' Parsing Index in :{response.url} ','yellow')
        wId = response.meta.get('wId')
        # Define how to parse the response
        # Extract all hrefs from links matching the CSS selector
        links = response.css(self.cfg['indexKey'])
        try:
            picurl = response.css(self.cfg['fmimg']).get()
            picurl = url_normalize(picurl)
            picurl = detectRealUrl(picurl, response.url, self.cfg)
            picraw = requests.get(picurl)
            with open(r'working/'+wId+'/rawcover.jpg', 'wb') as f:
                f.write(picraw.content)
                f.flush()
        except Exception as e:
            cprint(repr(e),'white',attrs=['dark'])
            # placeholder for default pic
            subprocess.run("cp cover.jpg working/%s/rawcover.jpg"%(wId),shell=True, check=True)
            cprint("无封面图片，采用自动生成",'red',attrs=['dark'])
        # Extract other book level info
        binfo = {
                'name':response.css(self.cfg['bookName']).get(),
                'author':response.css(self.cfg['authorName']).get(),
                }
        with open(r'working/'+wId+'/bookinfo', 'w', encoding='utf-8') as fp:
            json.dump(binfo,fp,ensure_ascii = False)
            fp.flush()

        file_path = r'working/'+wId+'/workingList'
        data = []
        # 清空List
        with open(file_path, 'w', encoding='utf-8') as fp:
            json.dump(data, fp, ensure_ascii=False, indent=4)

        # Iterate over each link and extract href and title
        for index,link in enumerate(links):
            url=response.urljoin(link.css(self.cfg['indexHrefKey']).get())
            title = link.css(self.cfg['indexTitleKey']).get()
            yield {
                'type': 'index',
                'url': url,
                'title': title.strip() if title else '',
                'wId': wId,
                'fId':"%05d_%s"%(index,hashlib.sha1((self.cfg['url']+url).encode("UTF-8")).hexdigest()[:10]),
            }
        if USEPLAYWRIGHT:
            if self.page and not self.page.is_closed():
                await self.page.close()


    async def parse_book(self, response):
        if USEPLAYWRIGHT: 
            self.page = response.meta["playwright_page"]

        # Define how to parse the response
        wId = response.meta.get('wId')
        fId = response.meta.get('fId')
        #print(response.css('#booktxt p::text').getall())
        curChar = chapter()
        curChar['type']='content'
        curChar['url']=response.url
        curChar['wId']=wId
        curChar['fId']=fId
        curChar['title']=response.css(self.cfg['titleKey']).get()
        curChar['content']=response.css(self.cfg['contentKey']).get()
        if USEPLAYWRIGHT:
            if self.page and not self.page.is_closed():
                await self.page.close()
        return curChar



    def epubRequest(self, request, response):
        self.logger.info(f"ePub Requesting:  {request.url}")
        request.cookies = self.cookie_dict
        request.meta["playwright"] = USEPLAYWRIGHT
        request.meta["playwright_include_page"] = USEPLAYWRIGHT
        request.meta["cookiejar"] = 1
        return request

    def noneRequest(self, request, response):
        self.crawler.stats.inc_value('index_stats')
        print("Not request further")
        return None



    def start_requests(self):
        if(self.mode=='index'):
            cprint("获取目录",'blue')
            for url in self.start_urls:
                wId = hashlib.sha1(url.encode("UTF-8")).hexdigest()[:10];
                cprint("创建工作目录",'blue',attrs=['dark'])
                subprocess.run("mkdir -p working/"+wId+"/dumps", shell=True, check=True)
                extra_meta = {'wId': wId}
                meta = {**self.custom_meta, **extra_meta}
                # GET request
                self.logger.info(f"Start to Request! {url}")
                yield scrapy.Request(
                        url=url,
                        cookies=self.cookie_dict,
                        meta = meta,
                        callback=self.parse_index,
                        #errback=self.errback_close_page,
                        )
        elif(self.mode=='content'):
            cprint("获取内容",'blue',attrs=['dark'])
            # start url已经获取完毕(__init__)
            for index,url in enumerate(self.start_urls):
                fId="%05d_%s"%(index,hashlib.sha1((self.cfg['url']+url).encode("UTF-8")).hexdigest()[:10])
                extra_meta = {'wId': self.wIdList[index], 'index':index, 'fId':fId}
                meta = {**self.custom_meta, **extra_meta}
                # GET request
                self.logger.info(f"Start to Request! {url}")
                yield scrapy.Request(
                        url=url,
                        cookies=self.cookie_dict,
                        meta = meta,
                        callback=self.parse_book,
                        )
