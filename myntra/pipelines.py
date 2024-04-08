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

        discounted_price = adapter.get('discounted_price')
        mrp = adapter.get('mrp')
        if discounted_price and mrp:
            adapter['discount_percentage'] = round((adapter['discount'] / mrp) * 100)

        coupon_code = adapter.get('coupon_code')
        if not coupon_code:
            adapter['coupon_code'] = None
            adapter['coupon_discount'] = None
            adapter['best_price'] = adapter['discounted_price']

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
            product_type VARCHAR(255),
            sub_category VARCHAR(255),
            master_category VARCHAR(255),
            best_price INTEGER,
            discounted_price INTEGER,
            mrp INTEGER,
            coupon_code VARCHAR(255),
            coupon_discount INTEGER,
            discount INTEGER,
            discount_percentage INTEGER,
            rating FLOAT,
            rating_count INTEGER,
            href TEXT
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

        args_str = ','.join(self.cur.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (adapter['name'], adapter['brand'], adapter['product_type'], adapter['sub_category'], adapter['master_category'], adapter['best_price'], adapter['discounted_price'], adapter['mrp'], adapter['coupon_code'], adapter['coupon_discount'], adapter['discount'], adapter['discount_percentage'], adapter['rating'], adapter['rating_count'], adapter['href'], scrape_id)).decode('utf-8') for adapter in self.products)
        self.cur.execute("""
        INSERT INTO products (name, brand, product_type, sub_category, master_category, best_price, discounted_price, mrp, coupon_code, coupon_discount, discount, discount_percentage, rating, rating_count, href, scrape_id)
        VALUES {}
        """.format(args_str))

        self.connection.commit()

        self.cur.close()
        self.connection.close()
