import scrapy
from news_scraper.items import BlogItem
from dateutil.parser import parse
import datetime
from scrapy.exceptions import CloseSpider

class HelpScoutSpider(scrapy.Spider):
    name = "helpscout"
    from_date = datetime.date.today() - datetime.timedelta(6*365/12)
    allowed_domains = ["helpscout.net"]
    start_urls = [
        "https://www.helpscout.net/blog/"
    ]

    def parse(self, response):
    	for href in response.xpath('//*[@id="post-list"]/div/div/a/@href'):
    		url = response.urljoin(href.extract())
    		yield scrapy.Request(url, callback=self.parse_dir_contents)

    	next_page = response.xpath("//a[contains(@class, 'next-page')]/@href")
    	if next_page:
    		print "NEXT PAGE!"
    		url = response.urljoin(next_page[0].extract())
    		yield scrapy.Request(url, self.parse)


    def parse_dir_contents(self, response):
    	item = BlogItem()
    	item['date'] = parse( response.xpath('//meta[@itemprop="datePublished"]/@content').extract()[0] ).date()
    	if item['date'] < self.from_date:
          raise CloseSpider('sufficient_data_gathered')
        item['title'] = response.xpath('//h1[@itemprop="headline"]/text()').extract()[0].strip()
    	item['url'] = response.url
    	item['author'] = response.xpath('//span[@itemprop="name"]/text()').extract()[0].strip()
    	item['contents'] = (" ").join(response.xpath('//div[@class="blog-post"]/p/text()').extract()).strip()
    	yield item