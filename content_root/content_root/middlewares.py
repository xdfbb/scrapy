# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import json
import logging
import sys

from scrapy import signals
from scrapy.crawler import logger

logger = logging.getLogger(__name__)

custom_isLoad = False
custom_useragent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'
custom_accessToken = '6D8CE288-3C7B-858B-8879-72C886F4A9B7_2C999066D114BC4F'
cookies = {'abtest_env': 'product', 'zsxq_access_token': '6D8CE288-3C7B-858B-8879-72C886F4A9B7_2C999066D114BC4F'}


class ContentRootDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    def __loadCustomInfo(self):
        global custom_isLoad
        global custom_useragent
        global custom_accessToken

        if custom_isLoad:
            return

        # options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        # options.add_argument('--disable-gpu')
        # options.add_argument('disable-infobars')
        # options.add_argument('--user-data-dir=./chrome-user-data')
        # driver = webdriver.Chrome(chrome_options=options)
        #
        # driver.get('https://wx.zsxq.com')
        # custom_accessToken = driver.get_cookie('zsxq_access_token')['value']
        logger.info('use accessToken is %s', custom_accessToken)
        # custom_useragent = driver.execute_script("return navigator.userAgent;").replace('HeadlessChrome', 'Chrome')
        logger.info('use user-agent is %s', custom_useragent)
        custom_isLoad = True
        # driver.close()

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        global custom_useragent
        global custom_accessToken
        global cookies

        self.__loadCustomInfo()

        request.headers.setdefault('user-agent', custom_useragent)
        request.cookies = cookies

        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.
        data = json.loads(response.body)
        if not data['succeeded']:
            logger.warning("cant process response, error code %d", data['code'])
        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


# useful for handling different item types with a single interface
class ContentRootSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
