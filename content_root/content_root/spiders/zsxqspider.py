import scrapy

group_page = "https://wx.zsxq.com/dweb2/index/group/551151485124"
files_page = 'https://wx.zsxq.com/dweb2/index/files'
group_files_page = "https://api.zsxq.com/v2/groups/551151485124/files?count=20"


class MySpider(scrapy.Spider):
    name = 'zsxq'

    def start_requests(self):
        return [scrapy.Request(group_files_page, callback=self.parse_files_page)]

    def parse_files_page(self, response):
        return [scrapy.Request(files_page, callback=self.parse_file_links)]

    def parse_file_links(self, response):
        response.
