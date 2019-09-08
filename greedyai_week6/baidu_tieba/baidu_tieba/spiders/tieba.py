# -*- coding: utf-8 -*-
import scrapy
from urllib import parse
from baidu_tieba.items import BaiduTiebaItem
import re


class TiebaSpider(scrapy.Spider):
    name = 'tieba'
    allowed_domains = ['tieba.baidu.com']
    start_urls = ['https://tieba.baidu.com/f?ie=utf-8&kw=dota2&fr=search']

    def parse(self, response):
        title_url_list = response.css('.j_th_tit::attr(href)').extract()

        if title_url_list:
            # 遍历每个连接，获取每篇帖子的具体数据
            for title_url in title_url_list:
                yield scrapy.Request(url=parse.urljoin(response.url, title_url), callback=self.parse_detail)

        # 获取下一页的url
        next_page_url = response.css('.next.pagination-item::attr(href)').extract()[0]
        if next_page_url:
            yield scrapy.Request(url=parse.urljoin(response.url, next_page_url), callback=self.parse_detail)

    def parse_detail(self, response):
        print(response.url)
        # 获取文章标题
        title = response.css('.core_title_txt.pull-left.text-overflow::text').extract()[0]
        # 获取回复的作者
        author_list = response.css('.p_author_name.j_user_card::text').extract()
        # 获取回复内容
        content_list = response.css('.d_post_content.j_d_post_content').extract()
        # 获取回复时间和楼层
        reply_time_and_floor_list = response.css('.post-tail-wrap span[class=tail-info]::text').extract()
        reply_time_and_floor_list = [each for each in reply_time_and_floor_list if each != '来自']
        # 筛选出回复时间
        replay_time_list = [reply_time_and_floor_list[i] for i in range(len(reply_time_and_floor_list)) if i % 2 == 1]
        # 筛选出楼层
        floor_list = [reply_time_and_floor_list[i] for i in range(len(reply_time_and_floor_list)) if i % 2 == 0]

        # 实例化item
        for i in range(len(author_list)):
            item = BaiduTiebaItem()
            item['title'] = title
            item['author'] = author_list[i]
            item['content'] = content_list[i]
            item['reply_time'] = replay_time_list[i]
            item['floor'] = floor_list[i]

            yield item

        page_tags_list = response.css('.l_pager.pager_theme_5.pb_list_pager a').extract()
        if page_tags_list:
            reg = '<a href="(.+)">'
            next_page_url = re.findall(reg, page_tags_list[-2])[0]
            yield scrapy.Request(url=parse.urljoin(response.url, next_page_url), callback=self.parse_detail)
