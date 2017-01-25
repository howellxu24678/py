# -*- coding: utf-8 -*-
import scrapy
from jandan.items import JandanItem


class JdSpider(scrapy.Spider):
    name = "jd"
    #allowed_domains = ["jandan.net/ooxx"]
    #allowed_domains = ["http://jandan.net/pic"]
    start_urls = (
        'http://jandan.net/pic/page-1#comments',
        #'http://www.topit.me/',
    )

    def errback(self, response):
        self.logger.error("response:%s", response)

    def parse(self, response):
        item = JandanItem()
        #item['image_urls'] = response.xpath('/html/body/div[2]/div[2]/div[1]/div[2]/ol/li[1]/div[1]/div/div[2]/p/a[1]').extract()
        #yield  item
        #image_urls = response.xpath('//img//@src').extract()#提取图片链接
        image_urls = response.xpath('//p//a[@class="view_img_link"]/@href').extract()
        self.logger.info('image_urls:%s', image_urls)
        item['image_urls'] = image_urls
        yield item

        new_url= response.xpath('//div[@class="cp-pagenavi"]//a//@href').extract_first()#翻页
        self.logger.info('new_url:%s', new_url)
        # print 'new_url',new_url
        if new_url:
            yield scrapy.Request(new_url,callback=self.parse, errback=self.errback)
