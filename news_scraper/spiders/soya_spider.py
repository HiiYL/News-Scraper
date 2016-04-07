import scrapy
from news_scraper.items import SoyaItem
from dateutil.parser import parse
import datetime
from scrapy.exceptions import CloseSpider

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class SoyaSpider(scrapy.Spider):
    name = "soya"
    from_date = datetime.date.today() - datetime.timedelta(1*365/12)
    allowed_domains = ["soyacincau.com"]
    start_urls = [
        "http://www.soyacincau.com"
    ]

    def parse(self, response):
      for href in response.xpath("//*[@id='content_wrapper']/div[1]/div/div[1]/h2/a/@href"):
        url = response.urljoin(href.extract())
        yield scrapy.Request(url, callback=self.parse_dir_contents)
      
      next_page = response.xpath("//a[contains(., 'Next Page')]/@href")
      if next_page:
          url = response.urljoin(next_page[0].extract())
          yield scrapy.Request(url, self.parse)


    def parse_dir_contents(self, response):
      item = SoyaItem()
      item['date'] = parse(response.xpath('//*[@id="content_wrapper"]/div[1]/div/div[1]/div[1]/div[1]/div/text()[1]').extract()[0], fuzzy=True).date()
      if item['date'] < self.from_date:
        raise CloseSpider('sufficient_data_gathered')
      item['url'] = response.url
      item['author'] = response.xpath('//*[@id="content_wrapper"]/div[1]/div/div[1]/div[1]/div[1]/div/a[1]/text()').extract()[0].strip()
      item['title'] = response.xpath('//*[@id="content_wrapper"]/div[1]/div/div[1]/div[1]/div[1]/h2/a/text()').extract()[0].strip()
      item['contents'] = ' '.join(response.xpath('//*[@id="content_wrapper"]/div[1]/div/div[1]/div[1]/p[position()<(last() - 1)]/text()').extract()).strip()
      item['categories'] = response.xpath('//*[@id="content_wrapper"]/div[1]/div/div[1]/div[1]/div[5]/table/tr[1]/td[2]/a/text()').extract()
      item['tags'] = response.xpath('//*[@id="content_wrapper"]/div[1]/div/div[1]/div[1]/div[5]/table/tr[2]/td[2]/span/a/text()').extract()
      # item['comments'] = response.xpath('//*[@id="idc-cover"]/div/div/div[2]/div/text()').extract()
      yield item

