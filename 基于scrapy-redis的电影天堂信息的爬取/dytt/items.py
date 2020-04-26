# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class DyttItem(scrapy.Item):
    # 电影译名
    translated = Field()
    # 电影片名
    title = Field()
    # 年代
    year = Field()
    # 产地
    country = Field()
    # 类别
    category = Field()
    # 语言
    language =Field()
    # 上映时间
    data = Field()
    # 豆瓣评分
    douban = Field()
    # 文件大小
    size = Field()
    # 片长
    movie_time = Field()
    # 导演
    director = Field()
    # 编剧
    screenwriter = Field()
    # 主演
    star = Field()
    # 标签
    label = Field()
    # 简介
    introduction = Field()
    # 下载地址
    download_link = Field()
    # 详细页面
    origin_url = Field()
    pass
