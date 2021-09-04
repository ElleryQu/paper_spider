# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os

from itemadapter import ItemAdapter
import scrapy
from scrapy.pipelines.files import FilesPipeline

from paper_spider.spiders.newspaper_navi_spider import base_headers, log_flag, id, storage_path
from paper_spider.utils.utils import path_join

class PdfPipeline(FilesPipeline):
    def get_media_requests(self, item, info):
        log_flag and print("PdfPipeline-> send request.")

        yield scrapy.Request(
            url     = item['pdf_url'], 
            headers = base_headers,
            meta    = {'uuid': item['uuid']},
            priority= 10
        )


    def file_path(self, request, response=None, info=None): # 修改文件名
        log_flag and print("PdfPipeline-> set file name.")

        filename = request.meta['uuid']

        # path_join(storage_path, 'pdf')  # 路径确保。
        # path_join(id, 'pdf', filename+'.pdf', is_file=True)
        return os.path.join(id, 'pdf', filename+'.pdf')   # 由爬虫负责路径确保。

    # def item_completed(self, results, item, info):      # 存入csv文件
    #     with open(path_join(storage_path, 'result.csv', is_file=True), 'a') as f:
    #         f.write(
    #             item['uuid' ]+','+\
    #             item['pdf_title']+','+\
    #             item['pdf_storage_path']+','+\
    #             item['txt_storage_path']+'\n'
    #         )

