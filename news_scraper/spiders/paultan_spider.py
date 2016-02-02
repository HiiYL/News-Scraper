import scrapy
from news_scraper.items import NewsScraperItem
from dateutil.parser import parse
import datetime
from scrapy.exceptions import CloseSpider

class PaulTanSpider(scrapy.Spider):
    name = "paultan"
    from_date = datetime.date.today() - datetime.timedelta(2*365/12)
    allowed_domains = ["paultan.org"]
    start_urls = [
        "http://www.paultan.org"
    ]

    def parse(self, response):
      for href in response.xpath('//*[@id="content"]/div/ul/li/article/*/a/@href'):
        url = response.urljoin(href.extract())
        yield scrapy.Request(url, callback=self.parse_dir_contents)
      
      next_page = response.xpath("//a[contains(., 'Next')][contains(@href,'page')]/@href")
      if next_page:
          url = response.urljoin(next_page[0].extract())
          yield scrapy.Request(url, self.parse)


    def parse_dir_contents(self, response):
      item = NewsScraperItem()
      item['date'] = parse(response.xpath('//*[@id="content"]/article/p/time/text()').extract()[0], fuzzy=True).date()
      if item['date'] < self.from_date:
        raise CloseSpider('sufficient_data_gathered')
      item['author'] = response.xpath('//*[@id="content"]/article/p/span[2]/a/text()').extract()[0].strip()
      item['title'] = response.xpath('//*[@id="content"]/article/h1/text()').extract()[0].strip()
      item['contents'] = ''.join(response.xpath('//*[@id="content"]/article/div[2]/p/text()').extract()).strip()
      yield item

