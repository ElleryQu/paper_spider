# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PdfItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    uuid                = scrapy.Field()
    pdf_url            = scrapy.Field()
    pdf_title           = scrapy.Field()
    pdf_storage_path    = scrapy.Field()
    txt_storage_path    = scrapy.Field()
    files               = scrapy.Field()