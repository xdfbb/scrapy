import json
import logging
from datetime import time

import scrapy

group_page = "https://wx.zsxq.com/dweb2/index/group/551151485124"
files_page = 'https://wx.zsxq.com/dweb2/index/files'
group_files_page = "https://api.zsxq.com/v2/groups/551151485124/files?count=20"
cookies = {'abtest_env': 'product', 'zsxq_access_token': '6D8CE288-3C7B-858B-8879-72C886F4A9B7_2C999066D114BC4F'}


class MySpider(scrapy.Spider):
    name = 'zsxq'

    def start_requests(self):
        return [scrapy.Request(group_files_page, callback=self.parse_files_page, cookies=cookies)]

    def parse_files_page(self, response):
        logging.info('调用返回对象 %s', response.text)
        json_response = json.loads(response.text)

        if (json_response['succeeded']):
            logging.info('成功返回对象，进行下载链接提取'),
            self.extract_links(json_response)
        else:
            logging.info('API返回空对象，停顿1秒继续尝试调用')
            time.sleep(1000)
            self.retry_requests

    def retry_requests(self):
        return [scrapy.Request(group_files_page, callback=self.parse_files_page, cookies=cookies)]

    def extract_links(self, json_response):
        logging.info('开始提取下载链接.......')
        for file in json_response['resp_data']['files']:
            logging.info(file)
