    def parse(self, response):
        for link in response.xpath("//h2[@class='entry-title']/a"):
            url = link.xpath("@href").extract()
            if parse( link.xpath("../../p/time/@datetime").extract()[0] ).date() < self.from_date:
                print "DONE " + str(url)
                done = True
                break
            else:
              yield scrapy.Request(url, callback=self.parse_dir_contents)

        next_page = response.xpath('//li[@class="active"]/following-sibling::li[1]/a/@href')
        if next_page and not done:
            print "NEXT PAGE!"
            url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(url, self.parse)