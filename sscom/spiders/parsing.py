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
    """
    Extracts data about a product from a web page.

    Args:
        response: The response object returned by the web page.

    Yields:
        A dictionary containing the extracted data for each product.
    """
    # Extract the location of the product from the web page.
    location = response.css('table.contacts_table tr:nth-child(4) td:nth-child(2)::text').get(default='')

    # Extract the specifications of the product from the web page.
    specs_table = response.css('table.options_list tr')
    specs = {}
    for spec in specs_table:
        spec_name = spec.xpath('./td[@class="ads_opt_name"]/text()').get()
        spec_value = spec.xpath('./td[@class="ads_opt"]/descendant::text()[normalize-space()]').get(default='')
        if spec_name and spec_value:
            specs[spec_name.strip()] = spec_value.strip()

    # Extract the photos of the product from the web page.
    photo_label = response.css('div.ads_photo_label')
    photos = photo_label.css('img.pic_thumbnail.isfoto::attr(src)').getall()

    # Extract the price and date of the product from the web page.
    price = response.css('span.ads_price::text').get(default='')
    date = response.css('td.msg_footer::text').get(default='')

    # Create a dictionary containing all the extracted data for the product.
    data = {
        'date': date.strip(),
        'price': price.strip(),
        'location': location.strip(),
        'specs': specs,
        'photos': photos,
    }

    # Yield the data for the product.
    yield data


class ParsingSpider(scrapy.Spider):
    name = "parsing"
    allowed_domains = ["ss.com"]
    start_urls = ["https://www.ss.com/msg/en/electronics/phones/mobile-phones/apple/iphone-14-pro-max/cbklco.html"]
    # start_urls = ["http://ss.com/en/electronics/"]

    def parse(self, response):
        # for category in get_categories(response):
        # for category in get_item_links(response):
        for category in get_item_data(response):
            yield category
        # get_item_links()
        # get_item_data(response)