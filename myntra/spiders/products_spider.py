import scrapy
from scrapy.utils.request import json
import w3lib.html

from myntra.items import ProductItem

class ProductsSpider(scrapy.Spider):
    name = "products"

    start_urls = ["https://www.myntra.com/"]

    fetch_count = 1

    def parse(self, response):
        product_type = None

        category_links = response.css(".desktop-categoryName, .desktop-categoryLink")

        self.logger.info(f"Fetched {len(category_links)} categories")

        for link in category_links:
            url = response.urljoin(link.css("::attr(href)").get())

            yield scrapy.Request(
                url,
                self.parse_category,
                meta={"playwright": True},
                cb_kwargs={ "total": len(category_links), },
            )

    def parse_category(self, response, total):
        self.logger.info(f"Processing category {response.url} [{self.fetch_count}/{total}]")

        self.fetch_count += 1

        scripts = response.css("script").getall()
        for script in scripts:
            if "searchData" in script:
                data = script.split('"searchData":')[1].split(',"seo":')[0]
                data = (data + "}")
                data = json.loads(data)

                products = data["results"]["products"]
                
                for product in products:
                    item = ProductItem()
                    item["name"] = product["productName"]
                    item["brand"] = product["brand"]
                    item["product_type"] = product["articleType"]["typeName"]
                    item["sub_category"] = product["subCategory"]["typeName"]
                    item["master_category"] = product["masterCategory"]["typeName"]
                    item["mrp"] = product["mrp"]
                    item["discounted_price"] = product["price"]
                    item["discount"] = product["discount"]
                    item["rating"] = product["rating"]
                    item["rating_count"] = product["ratingCount"]
                    item["href"] = product["landingPageUrl"]

                    if product["couponData"]:
                        item["best_price"] = product["couponData"]["couponDescription"]["bestPrice"]
                        item["coupon_code"] = product["couponData"]["couponDescription"]["couponCode"]
                        item["coupon_discount"] = product["couponData"]["couponDiscount"]

                    yield item

