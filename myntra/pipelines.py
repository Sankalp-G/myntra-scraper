# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os
from itemadapter.adapter import ItemAdapter

import humanfriendly
import psycopg2
import time
from dotenv import load_dotenv

load_dotenv()

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
                adapter[price_key] = float(value)

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
        else:
            adapter['discount'] = 0
            adapter['discount_percentage'] = 0

        return item

class SaveToPostgresPipeline:
    def __init__(self):
        hostname = os.getenv('DB_HOST')
        username = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')
        database = os.getenv('DB_NAME')
        port = os.getenv('DB_PORT')

        self.connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database, port=port)
        
        self.cur = self.connection.cursor()

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS scrapes(
            id serial PRIMARY KEY,
            start_time INTEGER,
            end_time INTEGER,
            products_count INTEGER
        )
        """)

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS products(
            id serial PRIMARY KEY, 
            scrape_id INTEGER REFERENCES scrapes(id) ON DELETE CASCADE ON UPDATE CASCADE,
            name VARCHAR(255),
            brand VARCHAR(255),
            category VARCHAR(255),
            product_type VARCHAR(255),
            price INTEGER,
            base_price INTEGER,
            rating DECIMAL,
            rating_count INTEGER,
            href VARCHAR(255),
            discount DECIMAL,
            discount_percentage DECIMAL
        )
        """)

        self.start_time = time.time()

        self.products = []

        self.connection.commit()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        self.products.append(adapter)

        return item

    def close_spider(self, spider):
        self.cur.execute("""
        INSERT INTO scrapes (start_time, end_time, products_count)
        VALUES (%s, %s, %s)
        RETURNING id
        """, (int(self.start_time), int(time.time()), len(self.products)))

        scrape_id = self.cur.fetchone()[0]

        args_str = ','.join(self.cur.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (adapter['name'], adapter['brand'], adapter['category'], adapter['product_type'], adapter['price'], adapter['base_price'], adapter['rating'], adapter['rating_count'], adapter['href'], adapter['discount'], adapter['discount_percentage'], scrape_id)).decode('utf-8') for adapter in self.products)
        self.cur.execute("""
        INSERT INTO products (name, brand, category, product_type, price, base_price, rating, rating_count, href, discount, discount_percentage, scrape_id)
        VALUES {}
        """.format(args_str))

        self.connection.commit()

        self.cur.close()
        self.connection.close()
