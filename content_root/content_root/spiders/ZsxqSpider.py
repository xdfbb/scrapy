import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class ZsxqSpider(CrawlSpider):
    name = 'zsxq'
    allowed_domains = ['wx.zsxq.com']
    start_urls = ['https://wx.zsxq.com/dweb2/index/group/551151485124']
    next_page='https://wx.zsxq.com/dweb2/index/files'

    rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        # Rule(LinkExtractor(allow=('category\.php',), deny=('subsection\.php',))),

        # Extract links matching 'item.php' and parse them with the spider's method parse_item
        Rule(LinkExtractor(allow=('/dweb2/index/files',)), callback='parse_item'),
    )

    def _parse(self, response, **kwargs):
         super(CrawlSpider,self)._parse(self, response, **kwargs)


    def parse_item(self, response):
        self.logger.info('Hi, this is an item page! %s', response.url)
        item = scrapy.Item()
        item['id'] = response.xpath('//td[@id="item_id"]/text()').re(r'ID: (\d+)')
        item['name'] = response.xpath('//td[@id="item_name"]/text()').get()
        item['description'] = response.xpath('//td[@id="item_description"]/text()').get()
        item['link_text'] = response.meta['link_text']
        url = response.xpath('//td[@id="additional_data"]/@href').get()
        return response.follow(url, self.parse_additional_page, cb_kwargs=dict(item=item))

    def parse_additional_page(self, response, item):
        item['additional_data'] = response.xpath('//p[@id="additional_data"]/text()').get()
        return item
