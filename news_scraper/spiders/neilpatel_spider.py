import scrapy
from news_scraper.items import BlogItem
from dateutil.parser import parse
import datetime
from scrapy.exceptions import CloseSpider

class NeilpatelSpider(scrapy.Spider):
    name = "neilpatel"
    from_date = datetime.date.today() - datetime.timedelta(1*365/12)
    allowed_domains = ["neilpatel.com"]
    start_urls = [
        "http://neilpatel.com/blog/"
    ]

    def parse(self, response):
      for href in response.xpath('//*[@id="article"]/div[2]/ul/li/a/@href'):
        url = response.urljoin(href.extract())
        

        if (url == 'http://neilpatel.com/'):
          raise CloseSpider('sufficient_data_gathered')
        else:
          date = parse(('-').join(url[21:-1].split('/')[:-1])).date()
          if date < self.from_date:
            raise CloseSpider('sufficient_data_gathered')
          else:
            yield scrapy.Request(url, callback=self.parse_dir_contents)

      # next_page = response.xpath("//a[@rel='next']/@href")
      # if next_page:
      #   print "NEXT PAGE!"
      #   url = response.urljoin(next_page[0].extract())
      #   yield scrapy.Request(url, self.parse)


    def parse_dir_contents(self, response):
      print "Test"

      item = BlogItem()
      item['date'] = parse(
        response.xpath('//*[@id="main"]/article/div[1]/p/text()').extract()[0].split("on")[1], fuzzy=True).date()
      # if item['date'] < self.from_date:
      #   raise CloseSpider('sufficient_data_gathered')
      item['title'] = ('').join(response.xpath('//*[@id="main"]/article/div[1]/h1/a/text()').extract())
      item['url'] = response.url
      item['author'] = response.xpath('//*[@id="main"]/article/div[1]/p/text()').extract()[0].split("on")[0][11:-1]
      item['contents'] = (' ').join(response.xpath('//*[@id="main"]/article/div[2]/p/text()').extract()).strip()
      yield item