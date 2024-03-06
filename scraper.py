import hrequests
from price_parser import Price
import unicodedata
import asyncio
import pandas as pd

BASE_URL = 'https://www.amazon.in/dp/'

# from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright

def scrape_data(asin: str):
    url = BASE_URL + asin
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        page.goto(url)

        try:
            page.wait_for_selector('div#titleSection')

            product_name_element = page.query_selector('div#titleSection')   
            product_name = product_name_element.text_content().strip()
        except:
            product_name = 'Element not found'
        print(product_name)

        try:
            discount_element = page.query_selector('span[class="a-size-large a-color-price savingPriceOverride aok-align-center reinventPriceSavingsPercentageMargin savingsPercentage"]')
            discount = discount_element.text_content()
            discount = abs(int(discount[:-1]))
        except:
            discount = 0
        print(discount)

        try:
            selling_price_element = page.query_selector('span[class="a-price aok-align-center reinventPricePriceToPayMargin priceToPay"]').text_content()
            # selling_price_value = selling_price_element.query_selector('span[class="a-price-whole"]').text_content()
            selling_price_value = Price.fromstring(selling_price_element).amount_float
        except:
            selling_price_value = 'Not available'
        print(selling_price_value)

        try:
            max_retail_price_element = page.query_selector('span[class="a-price a-text-price"]').text_content()
            # max_retail_price = max_retail_price_element.query_selector('span').text_content()
            max_retail_price = Price.fromstring(max_retail_price_element).amount_float
        except:
            max_retail_price = 'Not available'
        print(max_retail_price)

        product_specs = {}
        try:
            product_details = page.query_selector('div#prodDetails')
            specs = product_details.query_selector_all('table')

            for table in specs:
                for row in table.query_selector_all('tr'):
                    key = row.query_selector('th').text_content()
                    value = row.query_selector('td')
                    if key == 'Customer Reviews':
                        avg_rating = value.query_selector('a').query_selector('span').text_content().strip()
                        rating_count = value.query_selector('span#acrCustomerReviewText').text_content().strip()
                        continue

                    # Apply Unicode normalization
                    normalized_value = unicodedata.normalize('NFD', value.text_content().strip()).encode('ascii', 'ignore').decode('utf-8')
                    
                    product_specs[key] = normalized_value
        except:
            avg_rating = 'Not available'
            rating_count = 'Not available'
            product_specs = 'Not available'
            
        print(avg_rating, rating_count, product_specs)

        browser.close()

    df = pd.DataFrame()
    df['Product Name'] = [product_name]
    df['Discount'] = [discount]
    df['Selling Price'] = [selling_price_value]
    df['MRP'] = [max_retail_price]
    df['Average Rating'] = [avg_rating]
    df['Rating Count'] = [rating_count]
    df['Product Specs'] = [product_specs]

    df.to_csv('product_data.csv', index=False)

if __name__ == '__main__':

    # loop = asyncio.ProactorEventLoop()
    # asyncio.set_event_loop(loop)
    # loop.run_until_complete(scrape_data('B0BGS8PG3K'))

    scrape_data('B0BGS8PG3K')