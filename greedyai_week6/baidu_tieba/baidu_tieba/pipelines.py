# -*- coding: utf-8 -*-
import sqlite3
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class BaiduTiebaPipeline(object):
    # 当spider被执行时被调用
    def open_spider(self, spider):
        db_name = spider.settings.get('SQLITE_DBNAME', 'spider.db')

        self.db_con = sqlite3.connect(db_name)
        self.db_cur = self.db_con.cursor()

    # 当spider结束是被调用
    def close_spider(self, spider):
        self.db_con.commit()
        self.db_con.close()

    def process_item(self, item, spider):
        self.insert_db(item)
        return item

    # 写入数据库
    def insert_db(self, item):
        data = (
            item['title'],
            item['author'],
            item['content'],
            item['reply_time'],
            item['floor']
        )

        sql = 'INSERT INTO tb_baidu_tieba VALUES(?, ?, ?, ?, ?)'

        self.db_cur.execute(sql, data)
