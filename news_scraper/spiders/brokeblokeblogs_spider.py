import scrapy
from news_scraper.items import BlogItem
from dateutil.parser import parse
import datetime
from scrapy.exceptions import CloseSpider

class BrokeBlokeBlogsSpider(scrapy.Spider):
    name = "brokeblokeblogs"
    from_date = datetime.date.today() - datetime.timedelta(6*365/12)
    done = False
    allowed_domains = ["brokeblokeblogs.com"]
    start_urls = [
        "http://brokeblokeblogs.com/"
    ]

    def parse(self, response):
    	for href in response.xpath("//h2[@class='entry-title']/a/@href"):
    		url = response.urljoin(href.extract())
    		yield scrapy.Request(url, callback=self.parse_dir_contents)

    	next_page = response.xpath('//li[@class="active"]/following-sibling::li[1]/a/@href')
    	if next_page:
    		print "NEXT PAGE!"
    		url = response.urljoin(next_page[0].extract())
    		yield scrapy.Request(url, self.parse)


    def parse_dir_contents(self, response):
    	item = BlogItem()
    	item['date'] = parse( response.xpath('//time[@itemprop="datePublished"]/@datetime').extract()[0] ).date()
    	if item['date'] < self.from_date:
          raise CloseSpider('sufficient_data_gathered')
        item['title'] = response.xpath('//h1[@itemprop="headline"]/text()').extract()[0].strip()
    	item['url'] = response.url
    	item['author'] = response.xpath('//span[@class="entry-author-name"]/text()').extract()[0].strip()
    	item['contents'] = (" ").join(response.xpath('//div[@itemprop="text"]/p/text()').extract()).strip()
    	yield item