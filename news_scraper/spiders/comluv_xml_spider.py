from scrapy.spiders import SitemapSpider
from news_scraper.items import BlogItem
from dateutil.parser import parse
import datetime
from scrapy.exceptions import CloseSpider

class ComLuvSpider(SitemapSpider):
    name = 'comluv'
    sitemap_urls = ['http://comluv.com/post-sitemap2.xml']
    # namespaces = [
    #     ('sm', 'http://www.sitemaps.org/schemas/sitemap/0.9'),
    #     ]
    # itertag = 'sm:url'
    # iterator = 'iternodes'  # This is actually unnecessary, since it's the default value
    def hasXpath(xpath,response):
      response.xpath(xpath)

    def parse(self, response):
      item = BlogItem()
      # try:
      item['date'] = parse(response.xpath("//meta[@property='article:published_time']/@content").extract()[0]).date()
      # except IndexError:
        # item['date'] = parse(response.xpath('//*[@id="content"]/div[1]/div/div[2]/div/div[3]/article/div/div[1]/div/time/text()').extract()[0], fuzzy=True).date()

      # if item['date'] < self.from_date:
      #   raise CloseSpider('sufficient_data_gathered')
      item['url'] = response.url
      try:
        item['author'] = response.xpath('//a[@rel="author"]/text()').extract()[0].strip()
      except IndexError:
        item['author'] = ''
      item['title'] = response.xpath('//meta[@property="og:title"]/@content').extract()[0].strip()
      item['contents'] = ' '.join(response.xpath('//div[@class="entry-content"]/p/text()').extract()).strip()
      # item['categories'] = response.xpath('//*[@id="content"]/article/p/span[1]/a/text()').extract()
      yield item

    # def parse_node(self, response, node):
    #     self.logger.info('Hi, this is a <%s> node!: %s', self.itertag, ''.join(node.extract()))

    #     item = FoxMapItem()
    #     item['loc'] = node.xpath('loc').extract()
    #     # item['name'] = node.xpath('name').extract()
    #     # item['description'] = node.xpath('description').extract()
    #     return item