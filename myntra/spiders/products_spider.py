import scrapy
import w3lib.html


class ProductsSpider(scrapy.Spider):
    name = "products"

    start_urls = ["https://www.myntra.com/"]

    fetch_count = 0

    def parse(self, response):
        category_links = response.css(".desktop-categoryName, .desktop-categoryLink")

        self.logger.info(f"Fetched {len(category_links)} categories")

        for link in category_links:
            url = response.urljoin(link.css("::attr(href)").get())
            yield scrapy.Request(
                url,
                self.parse_category,
                meta={"playwright": True},
                cb_kwargs={
                    "category": link.css("::text").get(),
                    "total": len(category_links),
                },
            )

    def parse_category(self, response, category, total):
        products = response.css(".product-base")

        self.logger.info(
            f"Fetched {len(products)} products for category {category} [{self.fetch_count}/{total}]"
        )
        self.fetch_count += 1

        for product in products:
            yield {
                "name": product.css(".product-product::text").get(),
                "brand": product.css(".product-brand::text").get(),
                "category": category,
                "price": self.get_product_price(product),
                "basePrice": self.filter_html_tags(
                    product.css(".product-strike").get()
                ),
                "discount": product.css(".product-discountPercentage::text").get(),
                "rating": product.css(".product-ratingsContainer span::text").get(),
                "ratingCount": product.css(".product-ratingsCount::text").get(),
                "href": product.css("::attr(href)").get(),
            }

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
