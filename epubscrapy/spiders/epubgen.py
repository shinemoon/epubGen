USEPLAYWRIGHT = True
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import pdb

class EpubgenSpider(CrawlSpider):
    cfg= {
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
            "contentKey":"#content",
            "bookName":"#info h1",
            "authorName":"#info p:nth-child(2)",
            "titleKey":".bookname h1",
            "fetchDelay":2,
            "fmimg":"#fmimg img",
            "fmtype":"refine",
            "excludeKeys":["script","#content_tip","p"],
            #Mail
            "recmail":"shinemoon@foxmail.com",
            }

    name = "epubgenSpider"
    allowed_domains = cfg["domain"]
    handle_httpstatus_list = [404,500, 403]
    #Default URL for Demo Purpose
    start_urls = cfg["defaultUrl"]
    rules = [
            Rule(LinkExtractor(allow=(), unique=True,restrict_css=cfg["pageKey"]), process_request='epubRequest',callback='parse_index', follow=True),
            ]

    pdb.set_trace()

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

    cookie_dict = cfg["cookies"]

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
            "LOG_LEVEL": "INFO",
            "LOG_FILE_APPEND": False,
            "ITEM_PIPELINES" : {
                'epubscrapy.pipelines.EpubscrapyPipeline': 300,
                },
            "DEFAULT_REQUEST_HEADERS": custom_headers,
            }


    custom_settings = {**common_settings, **playwright_settings}

    def __init__(self, start_urls=None, *args, **kwargs):
        super(EpubgenSpider, self).__init__(*args, **kwargs)
#        pdb.set_trace()
#        print(f'========> {start_urls}')
        if start_urls is not None:
            self.start_urls = start_urls

    def parse(self, response):
        print('====================')
        print('   Default ')
        print('====================')
        print(response.url)
        pass

    def parse_index(self, response):
        print('====================')
        print(f' Parsing Index in :{response.url} ')
        print('====================')
        # Define how to parse the response
        # Extract all hrefs from links matching the CSS selector
        links = response.css(self.cfg['indexKey'])
        
        # Iterate over each link and extract href and title
        for link in links:
            href = link.css(self.cfg['indexHrefKey']).get()
            title = link.css(self.cfg['indexTitleKey']).get()
            yield {
                'href': response.urljoin(href),
                'title': title.strip() if title else ''
            }

    def parse_book(self, response):
        print('====================')
        print('   book ')
        print('====================')
        print(response.url)
        # Define how to parse the response
        pass

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
        for url in self.start_urls:
            # GET request
            self.logger.info(f"Start to Request! {url}")
            yield scrapy.Request(
                    url=url,
                    cookies=self.cookie_dict,
                    meta = self.custom_meta,
                    callback=self.parse_index,
                    )
