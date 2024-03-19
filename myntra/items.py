# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ProductItem(scrapy.Item):
    name = scrapy.Field()
    brand = scrapy.Field()
    category = scrapy.Field()
    product_type = scrapy.Field()
    price = scrapy.Field()
    basePrice = scrapy.Field()
    discount = scrapy.Field()
    rating = scrapy.Field()
    ratingCount = scrapy.Field()
    href = scrapy.Field()
    scrapeId = scrapy.Field()
