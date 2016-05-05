import scrapy
from news_scraper.items import BlogItem
from dateutil.parser import parse
import datetime
from scrapy.exceptions import CloseSpider

class HubSpotSpider(scrapy.Spider):
    name = "hubspot_marketing"
    from_date = datetime.date.today() - datetime.timedelta(1*365/12)
    allowed_domains = ["hubspot.com"]
    start_urls = [
        "https://blog.hubspot.com/marketing/"
    ]

    def parse(self, response):
    	for href in response.xpath('//*[@id="primary-blog-content"]/div/div/div/div/div[1]/div/div/div/div/div[1]/article/div[2]/a/@href'):
    		url = response.urljoin(href.extract())
    		yield scrapy.Request(url, callback=self.parse_dir_contents)

    	next_page = response.xpath("//a[@rel='next']/@href")
    	if next_page:
    		print "NEXT PAGE!"
    		url = response.urljoin(next_page[0].extract())
    		yield scrapy.Request(url, self.parse)


    def parse_dir_contents(self, response):
    	item = BlogItem()
    	item['date'] = parse(
    		response.xpath('//*[@id="primary-blog-content"]/div/div/div/div/div[1]/div/div/div/div/div[1]/p[1]/text()')
    		.extract()[0].strip().split(" // ")[0], fuzzy=True).date()
    	if item['date'] < self.from_date:
          raise CloseSpider('sufficient_data_gathered')
        item['title'] = response.xpath('//*[@id="hs_cos_wrapper_name"]/text()').extract()[0].strip()
    	item['url'] = response.url
    	item['author'] = response.xpath('//*[@id="hubspot-author_data"]/a[1]/text()').extract()[0].strip()
    	item['contents'] = (" ").join(response.xpath('//*[@id="hs_cos_wrapper_post_body"]/text()').extract()).strip()
    	yield item