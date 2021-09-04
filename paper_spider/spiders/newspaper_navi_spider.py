# -*- coding: utf-8 -*-

import time
import uuid
import re
import random
from pathlib import Path

import scrapy

from paper_spider.items import PdfItem
from paper_spider.settings import FILES_STORE
from paper_spider.utils.utils import path_join

'''
根据year_json构建post请求，得到特定年份所有日期的页面，parse解析每个日期对应的val值，作为day_json['date']的输入。
根据day_json构建post请求，得到特定日期特定页的目录，day_parse解析每个新闻的地址。
访问每个新闻的概述页，news_parse得到pdf下载和html的链接。
html_parse解析html页面的文本，转换为txt储存。
'''
id = 'np_navi'
log_flag = True                                 # 是否显示运行信息。
storage_path = Path(path_join(FILES_STORE, id)) # 爬取结果文件的存储路径。

year_count = 2                                  # 爬取自2021年来，year_count年的记录。

wengine_vpn_ticket = "e2b37898ee02bf55"         # 切换年份对应日期分组的时候，需要在cookie里传入此值以认证。
base_headers = {                                
    'Cookie'                    : 'show_vpn=0; wengine_vpn_ticket=%s; refresh=1' % wengine_vpn_ticket,     
}

year_json = {
    'pcode'                     : 'CCND',
    'py'                        : 'RMRB',
    'year'                      : ''
}          
year_url = "http://124.16.81.62/https/77726476706e69737468656265737421"\
    "fef657956933665b774687a98c/knavi/newspapers/data/group"

day_json = {
    'pcode'                     : 'CCND',
    'py'                        : 'RMRB',
    'pageIndex'                 : '',           # 页码，从1开始。
    'pageSize'                  : '20',
    'date'                      : ''
}
day_url = "http://124.16.81.62/https/77726476706e69737468656265737421"\
    "fef657956933665b774687a98c/knavi/newspapers/date/articles"

cm = re.compile("<[^>]+>")                      

# 重置csv，加表头。
with open(path_join(storage_path, 'result.csv', is_file=True), 'w') as f:   
    f.write('uuid,pdf_title,pdf_storage_path,txt_storage_path\n')


class NpNaviSpider(scrapy.Spider):              # Np for newspaper
    name = id

    def start_requests(self):
        for _ in range(year_count):
            year_json['year'] = str(2021-_)
            yield  scrapy.FormRequest(
                url             = year_url,
                headers         = base_headers,
                formdata        = year_json,
                callback        = self.parse
            )


    def parse(self, response):
        # 解析日期，以获得新闻列表。
        log_flag and print("Parse-> enter.")

        try:
            day_list = response.xpath('//dl[@class="jcsecondcol"]/dd/a/@value').extract()
        except:
            print("parse-> RAISED ERROR.")

        for date in day_list:
            day_json['date'] = date

            # 根据特定日期和页数组装post。猜测rmrb不会刊载超过80条新闻。max_page=2 or 4的情况可能产生未知的影响，待测试。
            for _ in range(4):
                day_json['pageIndex'] = str(_ + 1)

                yield scrapy.FormRequest(
                    url         = day_url,
                    headers     = base_headers,
                    formdata    = day_json,
                    callback    = self.day_parse,
                    priority    = 1
                )

    
    def day_parse(self, response):
        # 解析新闻链接。
        log_flag and print("Day_parse-> enter.")

        time.sleep(3+random.randint(0,2))

        try:
            news_list = response.xpath('//table[@class="tableStyle"]/tbody/tr/td[@class="name"]/a/@href').extract()
        except:
            print("day_parse-> RAISED ERROR.")

        for news_url in news_list:
            yield scrapy.Request(
                url             = "http://124.16.81.62"+news_url,
                headers         = base_headers,
                callback        = self.news_parse,
                priority        = 2 
            )


    def news_parse(self, response):
        # 下载pdf文件。
        log_flag and print("News_parse-> enter.")
        time.sleep(1)

        pdf_item = PdfItem()
        
        try:
            pdf_item['uuid'            ]    = str(uuid.uuid4())
            pdf_item['pdf_url'         ]    = response.xpath('//a[@id="pdfDown"]/@href').get()
            pdf_item['pdf_title'       ]    = response.xpath('//div[@class="wx-tit"]/h1').get()
            pdf_item['pdf_title'       ]    = cm.sub( '', pdf_item['pdf_title'] )
            pdf_item['pdf_storage_path']    = path_join(storage_path, 'pdf', pdf_item['uuid']+'.pdf', is_file=True)
            pdf_item['txt_storage_path']    = path_join(storage_path, 'txt', pdf_item['uuid']+'.txt', is_file=True)
            # log_flag and print(   'uuid            :     %s' % pdf_item['uuid'            ])
            # log_flag and print(   'pdf_url         :     %s' % pdf_item['pdf_url'         ])
            # log_flag and print(   'pdf_title       :     %s' % pdf_item['pdf_title'       ])
            # log_flag and print(   'pdf_storage_path:     %s' % pdf_item['pdf_storage_path'])
            # log_flag and print(   'txt_storage_path:     %s' % pdf_item['txt_storage_path'])

            with open(path_join(storage_path, 'result.csv', is_file=True), 'a') as f:
                f.write(
                    pdf_item['uuid' ]+','+\
                    pdf_item['pdf_title']+','+\
                    pdf_item['pdf_storage_path']+','+\
                    pdf_item['txt_storage_path']+'\n'
                )

        except:
            print("News_parse-> RAISED ERROR in PdfItem assembly.")

        yield pdf_item

        # 访问html页面。
        try:
            html_url = response.xpath('//li[@class="btn-html"]/a/@href').get()
        except:
            print("News_parse-> RAISED ERROR in html url extract.")
        yield scrapy.Request(
            url             = html_url,
            headers         = base_headers, 
            callback        = self.html_parse,
            meta            = {'uuid': pdf_item['uuid']},
            priority        = 10
        )
        

    def html_parse(self, response):
        log_flag and print("Html_parse-> enter.")

        # try:
        content = response.xpath('//div[@class="main"]/div[@class="content"]').get()

        # 删除script标签的内容，禁用beautifulsoap。
        pattern_script_b = r'<script'
        pattern_script_e = r'</script>'
        content_tmp = re.split(pattern_script_b, content)

        for _ in content_tmp:
            m = re.search(pattern_script_e, _)
            if m is not None:
                content += _[m.start()+9:]
            else:
                content = _
        # except:
        #     print("html_parse-> RAISED ERROR in html visit or pre-process.")

        # 解析页面文本。
        try:
            pattern_begin = 'brief start-->'
            pattern_end = '<!--brief end-->'
            m1 = re.search(pattern_begin, content)
            m2 = re.search(pattern_end, content)
            content = cm.sub( '', content[m1.start()+14: m2.start()] )

            # 干掉多余的空格和换行符。
            pattern_space = r'\s+'
            content = re.sub( pattern_space, r'\r\n', content)
        except:
            print("html_parse-> RAISED ERROR in text extract.")

        try:
            with open(path_join(storage_path,'txt',str(response.meta['uuid'])+'.txt', is_file=True),'w') as f:
                f.write(content)
        except:
            print("html_parse-> RAISED ERROR in IO.")
        

        