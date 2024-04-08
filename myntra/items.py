# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class ProductItem(scrapy.Item):
    name = scrapy.Field()
    brand = scrapy.Field()
    product_type = scrapy.Field()
    sub_category = scrapy.Field()
    master_category = scrapy.Field()
    best_price = scrapy.Field()
    discounted_price = scrapy.Field()
    mrp = scrapy.Field()
    coupon_code = scrapy.Field()
    coupon_discount = scrapy.Field()
    discount = scrapy.Field()
    discount_percentage = scrapy.Field()
    rating = scrapy.Field()
    rating_count = scrapy.Field()
    href = scrapy.Field()
    scrape_id = scrapy.Field()
