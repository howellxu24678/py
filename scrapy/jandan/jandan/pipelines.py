# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
# import os
# import urllib
# from jandan import settings
#
# class JandanPipeline(object):
#     def process_item(self, item, spider):
#         dir_path = '%s/%s' % (settings.IMAGES_STORE, spider.name)
#         print 'dir_path',dir_path
#
#         if not os.path.exists(dir_path):
#             os.makedirs(dir_path)
#
#         for image_url in item['image_urls']:
#             list_name = image_url.split('/')
#             file_name = list_name[len(list_name) - 1]
#
#             file_path = '%s/%s' % (dir_path, file_name)
#
#             # if os.path.exists(file_path):
#             #     continue
#             #
#             # with open(file_path, 'wb') as file_writer:
#             #     conn = urllib.urlopen(image_url)
#             #     file_writer.write(conn.read())
#             # file_writer.close()
#         return item


import scrapy
from scrapy.contrib.pipeline.images import ImagesPipeline
from scrapy.exceptions import DropItem

class JandanPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        for image_url in item['image_urls']:
            yield scrapy.Request(image_url)

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        print 'image_paths', image_paths
        if not image_paths:
            raise DropItem("Item contains no images")
        item['image_paths'] = image_paths
        return item
