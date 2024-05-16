USEPLAYWRIGHT = True
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

class EpubgenSpider(CrawlSpider):
    cfg= {
            "name":"香书小说",
            "url":"https://www.ibiquges.info",
            "indexKey":"#list dd a",
            "contentKey":"#content",
            "bookName":"#info h1",
            "authorName":"#info p:nth-child(2)",
            "titleKey":".bookname h1",
            "fetchDelay":2,
            "fmimg":"#fmimg img",
            "fmtype":"refine",
            "excludeKeys":["script","#content_tip","p"],
            "recmail":"shinemoon@foxmail.com"
            }
    name = "epubgen"
    allowed_domains = ["kuaishu5.com"]
    handle_httpstatus_list = [404,500, 403]
    start_urls = ["https://www.kuaishu5.com/b47875/"]
    rules = [
            #Rule(LinkExtractor(allow=(), restrict_css='#list #content_1 a'), process_request='epubRequest', callback='parse_book', follow=False),
            Rule(LinkExtractor(allow=(), restrict_css='.index-container-btn'), process_request='epubRequest',callback='parse_index', follow=True),
            ]

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

    cookie_dict = {'t':'64d056276329451626481e87d09e8340','r':'4079'}

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
                },
            "DEFAULT_REQUEST_HEADERS": custom_headers,
            }


    custom_settings = {**common_settings, **playwright_settings}

    def parse(self, response):
        print('====================')
        print('   Default ')
        print('====================')
        print(response.url)
        pass

    def parse_index(self, response):
        print('====================')
        print('   Index ')
        print('====================')
        print(response.url)
        # Define how to parse the response
        pass

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

    def start_requests(self):
        for url in self.start_urls:
            # GET request
            self.logger.info(f"Start to Request! {url}")
            yield scrapy.Request(
                url=url,
                cookies=self.cookie_dict,
                meta = self.custom_meta,
            )

