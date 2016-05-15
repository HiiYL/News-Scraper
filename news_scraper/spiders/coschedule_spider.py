import scrapy
from news_scraper.items import BlogItem
from dateutil.parser import parse
import datetime
from scrapy.exceptions import CloseSpider

class TemplateSpider(scrapy.Spider):
    name = "coschedule"
    from_date = datetime.date.today() - datetime.timedelta(6*365/12)
    allowed_domains = ["coschedule.com"]
    start_urls = [
        "http://coschedule.com/blog/"
    ]

    def parse(self, response):
        for href in response.xpath("//div[@class='blog-post-individual']/a[@class='kmq-blog-post-link']/@href"):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_dir_contents)

        next_page = response.xpath('//li[contains(@class,"previous")]/a/@href')
        if next_page:
            url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(url, self.parse)


    def parse_dir_contents(self, response):
        item = BlogItem()
        item['date'] = parse(response.xpath("//meta[@property='article:published_time']/@content").extract()[0]).date()
        if item['date'] < self.from_date:
          raise CloseSpider('sufficient_data_gathered')
        item['title'] = response.xpath('//meta[@property="og:title"]/@content').extract()[0].strip()
        item['url'] = response.url
        item['author'] = response.xpath('//meta[@name="author"]/@content').extract()[0].strip()
        item['contents'] = ("").join(response.xpath('//div[contains(@class, "post-content")]//p//text()').extract()).strip()
        yield item