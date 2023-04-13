import scrapy


def get_categories(response):
    # Extract all the h4 elements with class 'category'
    products = response.css('h4.category')

    # For each product element, extract the category name and link
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
    # Extract contact information from the web page.
    contacts_table = response.css('table.contacts_table tr')
    contacts = {}
    for contact in contacts_table:
        name = contact.xpath('.//td[@class="ads_contacts_name"]/text()').get('')
        value = contact.xpath('.//td[@class="ads_contacts"]//text()[normalize-space()] | .//a[@class="a9a"]/text()[normalize-space()]').getall()
        if name and value:
            # Check if the name already exists in the contacts dictionary, and append the new value.
            if name in contacts:
                contacts[name].append(''.join(value[:2]))
            else:
                contacts[name] = [''.join(value[:2])]

    # Extract product specifications from the web page.
    specs_table = response.css('table.options_list tr')
    specs = {}
    for spec in specs_table:
        spec_name = spec.xpath('./td[@class="ads_opt_name"]/text()').get()
        spec_value = spec.xpath('./td[@class="ads_opt"]/descendant::text()[normalize-space()]').get(default='')
        if spec_name and spec_value:
            specs[spec_name.strip()] = spec_value.strip()

    # Extract car specifications from the web page.
    cars_spec_table = response.css('div#msg_div_spec')
    car_specs = cars_spec_table.css('b.auto_c::text').getall()

    # Extract photo information from the web page.
    photo_label = response.css('div.ads_photo_label')
    photos = photo_label.css('img.pic_thumbnail.isfoto::attr(src)').getall()

    # Extract the price and date of the product from the web page.
    # Use xpath to get the price, as css selector is not working properly.
    price = response.xpath('(//span[@class="ads_price"] | //td[@class="ads_price"])/text()').get(default='')
    date = response.css('td.msg_footer::text').get(default='')

    # Create a dictionary containing all the extracted data for the product.
    data = {
        'date': date.strip(),
        'price': price.strip(),
        'contacts': contacts,
        'specs': specs,
        'car_specs': car_specs,
        'photos': photos,
    }

    yield data


class ParsingSpider(scrapy.Spider):
    name = "parsing"
    allowed_domains = ["ss.com"]
    start_urls = ["https://www.ss.com/msg/en/work/are-required/analyst/ifich.html"]
    # start_urls = ["http://ss.com/en/electronics/"]

    def parse(self, response):
        # for category in get_categories(response):
        # for category in get_item_links(response):
        for category in get_item_data(response):
            yield category
        # get_item_links()
        # get_item_data(response)