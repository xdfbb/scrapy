import scrapy
from scrapy.spiders import Spider

group_page = "https://wx.zsxq.com/dweb2/index/group/551151485124"
files_page = 'https://wx.zsxq.com/dweb2/index/files'


class ZsxqSpider(Spider):
    name = 'zsxq'


def start_requests(self):
    return scrapy.Request(group_page, callback=self.parse_files_page)


def parse_files_page(self, response):
    return scrapy.Request(files_page)
