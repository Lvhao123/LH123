# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy_redis.spiders import RedisSpider
from scrapy import Request
from dytt.items import DyttItem

#class DyttSpiderSpider(scrapy.Spider):
class DyttSpiderSpider(RedisSpider):
    name = 'dytt_spider'
    allowed_domains = ['dytt8.net']
    # start_urls = ['https://www.dytt8.net/html/gndy/dyzz/list_23_1.html']
    # 当使用redis时，start_urls就要从redis中获取，
    # 所以就要使用redis_key
    redis_key = "dytt_spider:start_urls"
    x = 0
    def parse(self, response):

        tables = response.xpath("//table[@class='tbspan']")
        for table in tables:
            detail_href = table.xpath(".//tr[2]/td[2]/b/a/@href").get()
            detail_url = response.urljoin(detail_href)
            title = table.xpath(".//tr[2]/td[2]/b/a/text()").get()
            #name = re.split(r'《|》',title)[1]
            yield Request(url=detail_url,callback=self.parse_item)

        self.x += 1
        print("正在爬取第%d页" % self.x)
        urls = response.xpath("//div[@class='co_content8']//a")
        for url in urls:
            if "下一页" in url.xpath(".//text()").get():
                url = url.xpath(".//@href").get()
                next_url = response.urljoin(url)
                yield Request(url=next_url,callback=self.parse)
            else:
                continue




    def parse_item(self, response):
        #print(response.text)
        item = DyttItem()
        ps = response.xpath("//div[@id='Zoom']//text()").getall()
        ps = "".join(ps)
        ps = re.split(r'◎',ps)
        del ps[0]
        for p in ps:
            if "译　　名" in p:
                p = re.split(r'名',p)
                item['translated'] = p[1].strip()
            elif "片　　名" in p:
                p = re.split(r'名', p)
                item['title'] = p[1].strip()
            elif "年　　代" in p:
                p = re.split(r"代",p)
                item['year'] = p[1].strip()
            elif "产　　地" in p:
                p = re.split(r"地",p)
                item['country'] = p[1].strip()
            elif "类　　别" in p:
                p = re.split(r"别",p)
                item['category'] = p[1].strip()
            elif "语　　言" in p:
                p = re.split(r"言",p)
                item['language'] = p[1].strip()
            elif "上映日期" in p:
                p = re.split(r'日期',p)
                item['data'] = p[1].strip()
            elif "豆瓣评分" in p:
                p = re.split(r'评分',p)
                item['douban'] = p[1].strip()
            elif "文件大小" in p:
                p = re.split(r'小',p)
                item['size'] = p[1].strip()
            elif "片　　长" in p:
                p = re.split(r'长',p)
                item['movie_time'] = p[1].strip()
            elif "导　　演" in p:
                p = re.split(r'演',p)
                item['director'] = p[1].strip()
            elif "编　　剧" in p:
                p = re.split(r'剧',p)
                item['screenwriter'] = p[1].strip()
            elif "主　　演" in p:
                p = re.split(r'演',p)
                item['star'] = p[1].strip()
            elif "标　　签" in p:
                p = re.split(r'签',p)
                item['label'] = p[1].strip()
            elif "简　　介" in p:
                p = re.split(r"简　　介|【下载地址】",p)
                item['introduction'] = p[1].strip()
            else:
                continue
        download_link = response.xpath("//div[@id='Zoom']//table//tr/td/a/@href").get()
        item['download_link'] = download_link
        item['origin_url'] = response.url
        yield item




