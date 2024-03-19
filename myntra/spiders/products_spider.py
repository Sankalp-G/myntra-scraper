from scrapy.utils.response import open_in_browser
import w3lib.html
import scrapy

class ProductsSpider(scrapy.Spider):
    name = "products"

    start_urls = ["https://www.myntra.com/"]

    def parse(self, response):
        category_links = response.css(".desktop-categoryName, .desktop-categoryLink")[0:1]

        yield from response.follow_all(category_links, self.parse_category, meta={"playwright": True})

    def parse_category(self, response):
        products = response.css(".product-base")

        for product in products:
            yield {
                "name": product.css('.product-product::text').get(),
                "brand": product.css('.product-brand::text').get(),
                "price": self.get_product_price(product),
                "basePrice": self.filter_html_tags(product.css('.product-strike').get()),
                "discount": product.css('.product-discountPercentage::text').get(),
                "rating": product.css('.product-ratingsContainer span::text').get(),
                "ratingCount": product.css('.product-ratingsCount::text').get(),
                "href": product.css('::attr(href)').get(),
            }

    def get_product_price(self, product):
        if product.css('.product-discountedPrice'):
            return self.filter_html_tags(product.css('.product-discountedPrice').get())
        else:
            return self.filter_html_tags(product.css('.product-price span').get())

    def filter_html_tags(self, html):
        if html:
            return w3lib.html.remove_tags(html)
        else:
            return None

