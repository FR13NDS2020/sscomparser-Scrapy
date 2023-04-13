import time

import scrapy


def get_categories(response):
    products = response.css('h4.category')
    for product in products:
        yield {
            'category_name': product.css('a.a_category').attrib['title'],
            'category_link': product.css('a.a_category').attrib['href'],
        }


def get_item_links(response, seen_links=set()):
    links = response.css('div.d1')
    for link in links:
        link_url = link.css('a.am::attr(href)').get()
        if link_url not in seen_links:
            seen_links.add(link_url)
            yield {'link': link_url}

    next_page = response.css('a.navi:last-of-type::attr(href)').get()

    if next_page and 'javascript' not in next_page:
        yield response.follow(next_page, callback=get_item_links, cb_kwargs={'seen_links': seen_links})


def get_item_data(response):
    contacts = response.css('table.contacts_table')
    options = response.css('table.options_list')
    car_spec = response.css('div#msg_div_spec')
    photo_label = response.css('div.ads_photo_label')
    photos = photo_label.css('a.attr(href)')
    price = response.css('span.ads_price::text').get()
    date = response.css('td.msg_footer::text').get()
    visits = response.css('#show_cnt_stat::text').get()
    yield {
        'date': date,
        'price': price,
        'photos': photos
        # 'photos': photos,
        # 'car_specs': car_spec,
        # 'options': options,
        # 'visits': visits
    }


class ParsingSpider(scrapy.Spider):
    name = "parsing"
    allowed_domains = ["ss.com"]
    start_urls = ["https://www.ss.com/msg/en/transport/cars/audi/a6/cigkm.html"]
    # start_urls = ["http://ss.com/en/electronics/"]


    def parse(self, response):
        # for category in get_categories(response):
        # for category in get_item_links(response):
        for category in get_item_data(response):
            yield category
        # get_item_links()
        # get_item_data(response)