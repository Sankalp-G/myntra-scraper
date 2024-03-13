import scrapy

class MyntraSpider(scrapy.Spider):
    name = "myntra"

    start_urls = ["https://www.myntra.com/"]

    def parse(self, response):
        last = None
        linkBuffer = []

        for link in response.css(".desktop-categoryName, .desktop-categoryLink"):
            if link.css(".desktop-categoryLink"):
                linkBuffer.append(link)

            if link.css(".desktop-categoryName"):
                if last == None:
                    last = link
                else:
                    yield self.format_link(last, linkBuffer)
                    last = link
                    linkBuffer = []
        else:
            yield self.format_link(last, linkBuffer)

    def format_link(self, link, sub = []):
        return {
            "name": link.css("::text").get(),
            "href": link.css("::attr(href)").get(),
            "sub": list(map(self.format_link, sub))
        }
