# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter.adapter import ItemAdapter

import humanfriendly

class ProductPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        field_names = adapter.field_names()
        for field_name in field_names:
            value = adapter.get(field_name)
            if value and isinstance(value, str):
                adapter[field_name] = value.strip()

        price_keys = ['price', 'base_price']
        for price_key in price_keys:
            value = adapter.get(price_key)
            if value and isinstance(value, str):
                value = value.replace("Rs. ", "").replace(",", "")
                adapter[price_key] = int(value)

        rating = adapter.get('rating')
        if rating:
            adapter['rating'] = float(rating)

        rating_count = adapter.get('rating_count')
        if rating_count:
            adapter['rating_count'] = humanfriendly.parse_size(rating_count)

        price = adapter.get('price')
        base_price = adapter.get('base_price')
        if price and base_price:
            adapter['discount'] = base_price - price
            adapter['discount_percentage'] = round((1 - price / base_price) * 100, 2)

        return item

