from price_parser import Price
import unicodedata
import asyncio
import pandas as pd
from playwright.async_api import async_playwright

BASE_URL = 'https://www.amazon.in/dp/'

async def scrape_data(asin: str):
    url = BASE_URL + asin

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(url)

        await page.wait_for_load_state('load')

        try:
            await page.wait_for_selector('div#titleSection')
            product_name_element = await page.query_selector('div#titleSection')
            product_name = await product_name_element.text_content()
            product_name = product_name.strip()
        except:
            product_name = 'Element not found'

        print(product_name)

        try:
            discount_element = await page.query_selector('span[class="a-size-large a-color-price savingPriceOverride aok-align-center reinventPriceSavingsPercentageMargin savingsPercentage"]')
            discount = await discount_element.text_content()
            discount = abs(int(discount[:-1]))
        except Exception as e:
            print('##################', e)
            discount = 0

        print(discount)

        try:
            selling_price_element = await (await page.query_selector('span[class="a-price aok-align-center reinventPricePriceToPayMargin priceToPay"]')).text_content()
            selling_price_value = Price.fromstring(selling_price_element).amount_float
        except Exception as e:
            print('###################', e)
            selling_price_value = 'Not available'

        print(selling_price_value)

        try:
            max_retail_price_element = await (await page.query_selector('span[class="a-price a-text-price"]')).text_content()
            # max_retail_price = await max_retail_price_element.query_selector('span').text_content()
            max_retail_price = Price.fromstring(max_retail_price_element).amount_float
        except Exception as e:
            print('#############################', e)
            max_retail_price = 'Not available'

        print(max_retail_price)

        product_specs = {}
        try:
            product_details = await page.query_selector('div#prodDetails')
            specs = await product_details.query_selector_all('table')

            for table in specs:
                for row in await table.query_selector_all('tr'):
                    key = await (await row.query_selector('th')).text_content()
                    value = await row.query_selector('td')

                    if key == 'Customer Reviews':
                        avg_rating = await value.query_selector('a')
                        avg_rating = await (await avg_rating.query_selector('span')).text_content()
                        avg_rating = avg_rating.strip()
                        rating_count = await (await value.query_selector('span#acrCustomerReviewText')).text_content()
                        rating_count = rating_count.strip()
                        continue

                    # Apply Unicode normalization
                    value = await value.text_content()
                    value = value.strip()
                    normalized_value = unicodedata.normalize('NFD', value).encode('ascii', 'ignore').decode('utf-8')
                    product_specs[key] = normalized_value
        except Exception as e:
            print('###############################', e)
            avg_rating = 'Not available'
            rating_count = 'Not available'
            product_specs = 'Not available'

        print(avg_rating)
        print(rating_count)
        print(product_specs)

        await browser.close()

    df = pd.DataFrame()
    df['Product Name'] = [product_name]
    df['Discount'] = [discount]
    df['Selling Price'] = [selling_price_value]
    df['MRP'] = [max_retail_price]
    df['Average Rating'] = [avg_rating]
    df['Rating Count'] = [rating_count]
    df['Product Specs'] = [product_specs]

    df.to_csv('product_data.csv', index=False)


def run_scraper(asin: str):
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(scrape_data(asin))
    
    # asyncio.run(scrape_data(asin))

if __name__ == '__main__':

    run_scraper('B0BGS8PG3K')