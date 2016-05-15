import scrapy
from news_scraper.items import BlogItem
from dateutil.parser import parse
import datetime
from scrapy.exceptions import CloseSpider

class ShoutmeloadSpider(scrapy.Spider):
    name = "kissmetrics"
    count = 0
    from_date = datetime.date.today() - datetime.timedelta(6*365/12)
    allowed_domains = ["kissmetrics.com"]
    start_urls = [
        "https://blog.kissmetrics.com/"
    ]

    def parse(self, response):

        for href in response.xpath("//h2/a[@rel='bookmark']/@href"):
            self.count = self.count + 1
            if self.count > 50:
                raise CloseSpider('sufficient_data_gathered')
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_dir_contents)

        next_page = response.xpath('//li[span[contains(@class, "current")]]/following-sibling::li[1]/a/@href')
        if next_page:
            url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(url, self.parse)


    def parse_dir_contents(self, response):
        item = BlogItem()
        # item['date'] = parse(response.xpath("//meta[@property='article:published_time']/@content").extract()[0]).date()
        # if item['date'] < self.from_date:
        #   raise CloseSpider('sufficient_data_gathered')
        item['title'] = response.xpath('//meta[@property="og:title"]/@content').extract()[0].strip()
        item['url'] = response.url
        if response.xpath('//a[@rel="author"]/text()'):
          item['author'] = (' ').join(response.xpath("//div[@class='entry-content']/p[last()]/text()").extract()[0].split(" ")[1:3]).strip()
        item['contents'] = ("").join(response.xpath('//div[contains(@class, "entry-content")]/p//text()').extract()).strip()
        yield item