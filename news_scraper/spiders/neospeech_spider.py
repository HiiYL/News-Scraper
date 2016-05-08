import scrapy
from news_scraper.items import BlogItem
from dateutil.parser import parse
import datetime
from scrapy.exceptions import CloseSpider

class NeilpatelSpider(scrapy.Spider):
    name = "neospeech"
    url_length = 0
    from_date = datetime.date.today() - datetime.timedelta(2*365/12)
    allowed_domains = ["neospeech.com"]
    start_urls = [
        "http://blog.neospeech.com/"
    ]

    def parse(self, response):
      self.url_length = len(response.url)
      for href in response.xpath('//div[@class="post_text_inner"]/h2/a/@href'):
        url = response.urljoin(href.extract())
        date = parse(('-').join(url[self.url_length:-1].split('/')[:-1])).date()
        if date < self.from_date:
          raise CloseSpider('sufficient_data_gathered')
        else:
          yield scrapy.Request(url, callback=self.parse_dir_contents)

      next_page = response.xpath("//li[@class='next']/a/@href")
      if next_page:
        print "NEXT PAGE!"
        url = response.urljoin(next_page[0].extract())
        yield scrapy.Request(url, self.parse)


    def parse_dir_contents(self, response):
      print "Test"

      item = BlogItem()
      item['date'] = parse(('-').join(response.url[25:-1].split('/')[:-1])).date()
      # if item['date'] < self.from_date:
      #   raise CloseSpider('sufficient_data_gathered')
      item['title'] = ('').join(response.xpath('//div[@class="post_content"]/h2/span/text()').extract())
      item['url'] = response.url
      item['author'] = response.xpath('//span[@class="post_author"]/a/span/text()').extract()[0]
      item['contents'] = (' ').join(response.xpath('//div[@class="post_content"]/p/span/text()').extract()).strip()
      yield item