import scrapy
from news_scraper.items import BlogItem
import dateparser
import datetime
from scrapy.exceptions import CloseSpider

class PowtoonSpider(scrapy.Spider):
    name = "powtoon"
    from_date = datetime.date.today() - datetime.timedelta(12*365/12)
    allowed_domains = ["powtoon.com"]
    start_urls = [
        "https://www.powtoon.com/blog/"
    ]

    def parse(self, response):
      for href in response.xpath("//div[@class='blog-item']/div/div/div/a/@href"):
        url = response.urljoin(href.extract())
        yield scrapy.Request(url, callback=self.parse_dir_contents)


      next_page = response.xpath('//li[@class="current"]/following-sibling::li[1]/a/@href')
      if next_page:
        print "NEXT PAGE!"
        url = response.urljoin(next_page[0].extract())
        yield scrapy.Request(url, self.parse)


    def parse_dir_contents(self, response):
      print "Test"
      item = BlogItem()
      item['date'] = dateparser.parse(response.xpath('//div[@class="meta-data"]/span[2]/text()').extract()[0].strip()).date()
      if item['date'] < self.from_date:
        raise CloseSpider('sufficient_data_gathered')
      item['title'] = ('').join(response.xpath('//h1[@class="post-title"]/text()').extract())
      item['url'] = response.url
      item['author'] = response.xpath('//div[@class="meta-data"]/span[1]/text()').extract()[0].strip()
      item['contents'] = (' ').join(response.xpath('//div[@class="entry"]/p/text()').extract()).strip()
      yield item