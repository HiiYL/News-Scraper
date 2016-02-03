from scrapy.spiders import SitemapSpider
from news_scraper.items import FoxItem
from dateutil.parser import parse
import datetime
from scrapy.exceptions import CloseSpider

class MySpider(SitemapSpider):
    name = 'foxnews'
    sitemap_urls = ['http://www.foxnews.com/sitemap.xml?idx=33']
    # namespaces = [
    #     ('sm', 'http://www.sitemaps.org/schemas/sitemap/0.9'),
    #     ]
    # itertag = 'sm:url'
    # iterator = 'iternodes'  # This is actually unnecessary, since it's the default value
    def hasXpath(xpath,response):
      response.xpath(xpath)

    def parse(self, response):
      item = FoxItem()
      # try:
      item['date'] = parse(response.xpath('//meta[@name="dc.date"]/@content').extract()[0], fuzzy=True).date()
      # except IndexError:
        # item['date'] = parse(response.xpath('//*[@id="content"]/div[1]/div/div[2]/div/div[3]/article/div/div[1]/div/time/text()').extract()[0], fuzzy=True).date()

      # if item['date'] < self.from_date:
      #   raise CloseSpider('sufficient_data_gathered')
      item['url'] = response.url
      try:
        item['author'] = response.xpath('//meta[@name="dc.creator"]/@content').extract()[0].strip()
      except IndexError:
        item['author'] = ''
      item['title'] = response.xpath('//meta[@name="dc.title"]/@content').extract()[0].strip()
      item['contents'] = ' '.join(response.xpath('//*[@id="content"]/div[1]/div[3]/article/div/div[3]/div[2]/p/text()').extract()).strip()
      # item['categories'] = response.xpath('//*[@id="content"]/article/p/span[1]/a/text()').extract()
      yield item

    # def parse_node(self, response, node):
    #     self.logger.info('Hi, this is a <%s> node!: %s', self.itertag, ''.join(node.extract()))

    #     item = FoxMapItem()
    #     item['loc'] = node.xpath('loc').extract()
    #     # item['name'] = node.xpath('name').extract()
    #     # item['description'] = node.xpath('description').extract()
    #     return item