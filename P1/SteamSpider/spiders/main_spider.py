import scrapy
import re

# 1) Вытянуть платформы
# 2) Вытянуть разные ссылки
# 3) Отличающиеся страницы

class SteamSpider(scrapy.Spider):
    name = 'little_spiderok'
    pages = 2  # at least 1
    # link = 'https://store.steampowered.com/search/?sort_by=&sort_order=0&term=strategy&supportedlang=russian&page='  # strategy
    # link = 'https://store.steampowered.com/search/?sort_by=&sort_order=0&term=shooter&supportedlang=russian&page='  # shooters
    link = 'https://store.steampowered.com/search/?sort_by=&sort_order=0&term=souls%20like&supportedlang=russian&page='  # souls_like
    start_urls = [link + '1']

    def parse(self, response):
        for l in response.xpath('//a[@data-gpnav="item"]/@href'):
            yield response.follow(l, callback=self.parse_page)

        for i in range(2, SteamSpider.pages + 1):
            yield response.follow(SteamSpider.link + str(i), callback=self.parse)

    def parse_page(self, response):
        to_path = []
        for i in response.xpath('//div[@class="blockbg"]/a/text()'):
            to_path.append(i.get())
        to_path = to_path[1:]
        data = response.xpath('//div[@class="date"]/text()').get()
        if data and int(data.split()[2]) <= 2000:
            return
        yield {
            'title': response.xpath('//div[@id="appHubAppName_responsive"]/text()').get(),
            'path': '/'.join(to_path),
            'reviews': ' '.join([x.get() for x in response.xpath('//div[@class="summary_section"]/span/text()')]),
            'release date': data,
            'developer': response.xpath('//div[@id="developers_list"]/a/text()').get(),
            'popular tags': ', '.join(
                [x.get().strip() for x in response.xpath('//div[@class="glance_tags popular_tags"]/a/text()')]),
            'price':  response.xpath('//div[@class="discount_final_price"]/text() | //div[@class="game_purchase_price price"]/text()').get().strip(),
            'platforms available': ', '.join([x.get().strip() for x in response.xpath('//div[@class="sysreq_contents"]/div/@data-os')])
        }
# response.xpath('//a[@data-gpnav="item"]/@href')[20].get()
