import scrapy
import w3lib.html

from myntra.items import ProductItem

class ProductsSpider(scrapy.Spider):
    name = "products"

    start_urls = ["https://www.myntra.com/"]

    fetch_count = 0

    def parse(self, response):
        product_type = None

        category_links = response.css(".desktop-categoryName, .desktop-categoryLink")[0:20]

        self.logger.info(f"Fetched {len(category_links)} categories")

        for link in category_links:
            url = response.urljoin(link.css("::attr(href)").get())

            if link.css(".desktop-categoryName"):
                product_type = link.css("::text").get()

            yield scrapy.Request(
                url,
                self.parse_category,
                meta={"playwright": True},
                cb_kwargs={
                    "category": link.css("::text").get(),
                    "product_type": product_type,
                    "total": len(category_links),
                },
            )

    def parse_category(self, response, category, total, product_type):
        products = response.css(".product-base")

        self.logger.info(
            f"Fetched {len(products)} products for category {category} [{self.fetch_count}/{total}]"
        )
        self.fetch_count += 1

        for product in products:
            p = ProductItem()
            p["name"] = product.css(".product-product::text").get()
            p["brand"] = product.css(".product-brand::text").get()
            p["category"] = category
            p["product_type"] = product_type
            p["price"] = self.get_product_price(product)
            p["basePrice"] = self.filter_html_tags(
                product.css(".product-strike").get()
            )
            # p["discount"] = product.css(".product-discountPercentage::text").get()
            p["rating"] = product.css(".product-ratingsContainer span::text").get()
            p["ratingCount"] = product.css(".product-ratingsCount::text").get()
            p["href"] = product.css("::attr(href)").get()
            yield p


    def get_product_price(self, product):
        if product.css(".product-discountedPrice"):
            return self.filter_html_tags(product.css(".product-discountedPrice").get())
        else:
            return self.filter_html_tags(product.css(".product-price span").get())

    def filter_html_tags(self, html):
        if html:
            return w3lib.html.remove_tags(html)
        else:
            return None
