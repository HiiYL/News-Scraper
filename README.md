# News-Scraper
A Python script to download news from a collection of news sources. Written with Scrapy.

Also included is a script to perform LDA on the downloaded articles.


### USAGE
##### Scraping:
Spiders Provided:

1. Soya ( Soyacincau.com )
2. paultan ( Paultan.org )
3. foxnews ( Foxnews.com )

To Use:

``` scrapy crawl [ spider-name ] [ -o output-file ] [ -t output-file-type ]```

##### Running LDA:
1. Using the csv output from previous step, use:

   ``` simple_lda.py -i FILENAME [-s {none,porter,porter2}] [-ni NUM_ITER] [ -twc TOPWORDS_COUNT ]```
