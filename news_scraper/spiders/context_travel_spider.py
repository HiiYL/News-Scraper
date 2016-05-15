import scrapy
from news_scraper.items import BlogItem
from dateutil.parser import parse
import datetime
from scrapy.exceptions import CloseSpider

class ShoutmeloadSpider(scrapy.Spider):
    name = "context_travel"
    from_date = datetime.date.today() - datetime.timedelta(6*365/12)
    allowed_domains = ["contexttravel.com"]
    start_urls = [
        "http://blog.contexttravel.com"
    ]

    def parse(self, response):
        for href in response.xpath("//h2/a[@rel='bookmark']/@href"):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_dir_contents)

        next_page = response.xpath('//div[@class="alignright"]/a/@href')
        if next_page:
            url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(url, self.parse)


    def parse_dir_contents(self, response):
        item = BlogItem()
        item['date'] = parse(response.xpath("//p[@class='post-date']/text()").extract()[0]).date()
        if item['date'] < self.from_date:
          raise CloseSpider('sufficient_data_gathered')
        item['title'] = response.xpath('//meta[@property="og:title"]/@content').extract()[0].strip()
        item['url'] = response.url
        if response.xpath('//span[@class="entry-author-name"]/text()'):
          item['author'] = response.xpath('//p[@class="post-author"]/a/text()').extract()[0].strip()
        item['contents'] = ("").join(response.xpath('//div[contains(@class, "post-content")]/p//text()').extract()).strip()
        yield item