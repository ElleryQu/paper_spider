# 完整测试
# 初始化 √
import time
import uuid
import re
import random
import os
from pathlib import Path

import scrapy

from paper_spider.items import PdfItem

log_flag = True                                 # 是否显示运行信息。
storage_path = Path(r'result\np_navi')          # 爬取结果文件的存储路径。

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


def path_join(path, *paths, is_file=False):
    '''
    拼接路径。如果路径目录不存在，则生成其目录。如果对象是文件目录且目录不存在，则生成其父目录。
    '''
    p = os.path.join(path, *paths)

    if is_file:
        os.makedirs(os.path.dirname(p), exist_ok=True)
    else:
        os.makedirs(p, exist_ok=True)

    return p


# start_request √
year_json['year']='2021'
req=scrapy.FormRequest(
    url             = year_url,
    headers         = base_headers,
    formdata        = year_json
)
fetch(req)

# parse √
day_list = response.xpath('//dl[@class="jcsecondcol"]/dd/a/@value').extract()
day_json['date'] = day_list[0]
day_json['pageIndex'] = '1'
preq=scrapy.FormRequest(
    url         = day_url,
    headers     = base_headers,
    formdata    = day_json
)
fetch(preq)

# day_parse √
news_list = response.xpath('//table[@class="tableStyle"]/tbody/tr/td[@class="name"]/a/@href').extract()
news_val = news_list[0]
dpreq=scrapy.Request(
    url             = "http://124.16.81.62"+news_val,
    headers         = base_headers    
)
fetch(dpreq)

# news_parse pdf 与news_parse html测试冲突 ?
pdf_item = PdfItem()
pdf_item['pdf_url'         ]    = response.xpath('//a[@id="pdfDown"]/@href').get()
nppreq = scrapy.Request(
    url     = pdf_item['pdf_url'], 
    headers = base_headers
)
fetch(nppreq)

# news_parse html √
html_url = response.xpath('//li[@class="btn-html"]/a/@href').get()
nphreq = scrapy.Request(
    url             = html_url,
    headers         = base_headers
)
fetch(nphreq)

# html_parse √ 
content = response.xpath('//div[@class="main"]/div[@class="content"]').get()

pattern_script_b = r'<script'
pattern_script_e = r'</script>'
content_tmp = re.split(pattern_script_b, content)
for _ in content_tmp:
    m = re.search(pattern_script_e, _)
    if m is not None:
        content += _[m.start()+9:]
    else:
        content = _
pattern_begin = 'brief start-->'
pattern_end = '<!--brief end-->'
m1 = re.search(pattern_begin, content)
m2 = re.search(pattern_end, content)
content = cm.sub( '', content[m1.start()+14: m2.start()] )
# 干掉多余的空格和换行符。
pattern_space = r'\s+'
content = re.sub( pattern_space, r'\r\n', content)
with open(path_join(storage_path,'txt','1.txt', is_file=True),'a') as f:
    f.write(content)



# 1. 在scrapy shell测试按照年份获取日期分组是否成功
# 4 400（强）；1,2,3,5 重定向至124.16.81.62；0 500状态码；这是一个cookie的问题！
base_json = {
    'pcode'                     : 'CCND',
    'py'                        : 'RMRB',
    'year'                      : '2019'  
} 
wengine_vpn_ticket = "7c34801a7b92c35b"             # 切换年份对应日期分组的时候，需要在cookie里传入此值。似乎与时间有关。
base_headers = {        
    # 'Accept'                    : '*/*',
    # 'Accept-Encoding'           : 'gzip, deflate',
    # 'Accept-Language'           : 'zh-CN,zh;q=0.9,en;q=0.8',
    # # 'Content-Length'            : '28',             # 加入此值会导致400状态码
    # 'Content-Type'              : 'application/x-www-form-urlencoded; charset=UTF-8',
    'Cookie'                    : 'wengine_vpn_ticket=%s' % wengine_vpn_ticket,     # wengine_vpn_ticket会变，机制及作用不明
    # 'DNT'                       : '1',
    # 'Host'                      : '124.16.81.62',
    # 'Connection'                : 'keep-alive',
    # 'Origin'                    : 'http://124.16.81.62',
    # 'Referer'                   : 'http://124.16.81.62/https/77726476706e69737468656265737421fef657956933665b774687a98c/knavi/newspapers/RMRB/detail',
    # 'X-Requested-With'          : 'XMLHttpRequest'
    # 'Upgrade-Insecure-Requests' : 1 # error
}
base_url = "http://124.16.81.62/https/77726476706e69737468656265737421"\
    "fef657956933665b774687a98c/knavi/newspapers/data/group"
req = scrapy.FormRequest(url=base_url,formdata=base_json,headers=base_headers)
req = scrapy.FormRequest(url=day_url,formdata=day_json,headers=base_headers)
fetch(req)

day_json = {
    'pcode'                     : 'CCND',
    'py'                        : 'RMRB',
    'pageIndex'                 : '1',           # 从1开始
    'pageSize'                  : '20',
    'date'                      : '2wa1vw8q_b2M_x5KH-cXjdMKeN6B5cZz5TTmNTCGWm06pjA6HwqdKsUs6ZDBAwuvJWqfiOl2ehs='
}

n_url='http://124.16.81.62/https/77726476706e69737468656265737421fef657956933665b774687a98c/knavi/Detail/RedirectPage?sfield=FN&v=jPi7yECjqOzSrniCGMnJyJfKRUIu9ebiR5InXcAVMMM-4DRI-SAzTOSO9-yt4ILEOEiT3iiIFPj6LtJ9VfXkF5OST0ES45GlftS65tlqiYNNy7tpo0lMGmUgUefISU8D&uniplatform=NZKPT'

view(response)


