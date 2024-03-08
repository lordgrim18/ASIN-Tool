import asyncio
import unicodedata
import pandas as pd
from price_parser import Price
from playwright.async_api import async_playwright

BASE_URL = 'https://www.amazon.in/dp/'

async def get_product_name(page):
    try:
        await page.wait_for_selector('div#titleSection')
        product_name_element = await page.query_selector('div#titleSection')
        product_name = await product_name_element.text_content()
        product_name = product_name.strip()
    except Exception as e:
        # print('Error in finding product name:', e)
        product_name = 'Element not found'

    return product_name

async def get_product_price_discount(page):
    try:
        selling_price_element = await (await page.query_selector('span[class="a-price aok-align-center reinventPricePriceToPayMargin priceToPay"]')).text_content()
        selling_price_value = Price.fromstring(selling_price_element).amount_float

        currency_used = Price.fromstring(selling_price_element).currency

        max_retail_price_element = await (await page.query_selector('span[class="a-price a-text-price"]')).text_content()
        # max_retail_price = await max_retail_price_element.query_selector('span').text_content()
        max_retail_price = Price.fromstring(max_retail_price_element).amount_float

    except:
        try:
            # price_parent_element = await page.query_selector(":text('M.R.P') >> .. >> .. >> .. >> ..")
            selling_price_element = await page.query_selector('span[class="a-price a-text-price a-size-medium apexPriceToPay"]')
            selling_price = await selling_price_element.text_content()
            selling_price_value = Price.fromstring(selling_price).amount_float
            currency_used = Price.fromstring(selling_price).currency

            mrp_discount_element = await page.query_selector_all('span[class="a-price a-text-price a-size-base"]')
            max_retail_price = (
            Price.fromstring(await mrp_discount_element[0].text_content()).amount_float
            if  mrp_discount_element
            else selling_price_value
            )

        except Exception as e:
            # print('Error in finding price:' ,e)
            selling_price_value = 'Not available'
            currency_used = 'Not available'
            max_retail_price = 'Not available'

    discount = round(((
        max_retail_price - selling_price_value) / max_retail_price) * 100
        ) if selling_price_value != 'Not available' else 'Not available'
    
    return selling_price_value, max_retail_price, currency_used, discount

async def get_avg_rating(page):
    try:
        avg_rating = await (await page.query_selector('span[data-hook="rating-out-of-text"]')).text_content()
        avg_rating = avg_rating.strip()
        avg_rating = avg_rating.split(' ')[0]
    except Exception as e:
        # print('Error in finding average rating:', e)
        avg_rating = 'Not available'

    return avg_rating

async def get_rating_count(page):
    try:
        rating_count = await (await page.query_selector('span[data-hook="total-review-count"]')).text_content()
        rating_count = rating_count.strip()
        rating_count = rating_count.split(' ')[0]
    except Exception as e:
        # print('Error in finding total ratings:', e)
        rating_count = 'Not available'

    return rating_count

async def get_product_specs(page):
    product_specs = {}
    try:
        product_details = await page.query_selector('div#prodDetails')
        specs = await product_details.query_selector_all('table')

        for table in specs:
            for row in await table.query_selector_all('tr'):
                key = await (await row.query_selector('th')).text_content()
                key = key.strip()
                value = await row.query_selector('td')

                if key == 'ASIN':
                    continue

                if key == 'Customer Reviews':
                    continue

                # Apply Unicode normalization
                value = await value.text_content()
                value = value.strip()
                normalized_value = unicodedata.normalize('NFD', value).encode('ascii', 'ignore').decode('utf-8')
                product_specs[key] = normalized_value


    except:
        try:
            product_details_parents = await page.query_selector_all(":text('Product details') >> ..")

            product_details_elements = await product_details_parents[0].query_selector_all("div[class='a-fixed-left-grid product-facts-detail']")
            for product_details_element in product_details_elements:
                product_details_element = await product_details_element.query_selector("div")
                product_details = await product_details_element.query_selector_all("div")
                key = await product_details[0].text_content()
                key = key.strip()
                if key == 'ASIN':
                    continue
                value = await product_details[1].text_content()
                value = value.strip()
                normalized_value = unicodedata.normalize('NFD', value).encode('ascii', 'ignore').decode('utf-8')
                product_specs[key] = normalized_value
        
            product_details_elements = await product_details_parents[1].query_selector_all("ul")
            product_details_lists = await product_details_elements[0].query_selector_all("li")
            for product_details_list in product_details_lists:
                product_details = await product_details_list.query_selector("span")
                product_details = await product_details.query_selector_all("span")
                key = await product_details[0].text_content()
                key = key.strip()
                normalized_key = unicodedata.normalize('NFD', key).encode('ascii', 'ignore').decode('utf-8')
                normalized_key = normalized_key.replace(':', '')
                normalized_key = normalized_key.strip()
                if normalized_key == 'ASIN':
                    continue
                value = await product_details[1].text_content()
                value = value.strip()
                normalized_value = unicodedata.normalize('NFD', value).encode('ascii', 'ignore').decode('utf-8')
                product_specs[normalized_key] = normalized_value

        except Exception as e:
            # print('Error in finding specifications:', e)
            product_specs = 'Not available'

    return product_specs
            

async def scrape_data(asin: str):
    url = BASE_URL + asin

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url)
        await page.wait_for_load_state('load')

        if await page.query_selector(":has-text('The Web address you entered is not a functioning page on our site.')"):
            print('Invalid ASIN')
            df = pd.DataFrame()
            df['ASIN'] = ['Invalid ASIN']
            df.to_csv('./data/product_data.csv', index=False)
            return 

        df = pd.DataFrame()
        df['ASIN'] = [asin]
        df['product_name'] = [await get_product_name(page)]
        selling_price_value, max_retail_price, currency_used, discount = await get_product_price_discount(page)
        df['discount'] = [discount]
        df['selling_price'] = [selling_price_value]
        df['MRP'] = [max_retail_price]
        df['currency_used'] = [currency_used]
        df['average_rating'] = [await get_avg_rating(page)]
        df['rating_count'] = [await get_rating_count(page)]
        df['product_specs'] = [await get_product_specs(page)]

        await browser.close()

    df.to_csv('./data/product_data.csv', index=False)


def run_scraper(asin: str):
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(scrape_data(asin))

    # asyncio.run(scrape_data(asin))

if __name__ == '__main__':

    # run_scraper('B0BGS8PG3K')
    # run_scraper('B083FQS2GZ')
    # run_scraper('B0CRDDTQXS')
    # run_scraper('B0CPYJJJMM')
    # run_scraper('B077BFH786')
    # run_scraper('B07M9XYH9K')
    # run_scraper('B08D8J88X3')
    # run_scraper('B09CKWH7W3')
    run_scraper('B0C9HXT93P')
    # run_scraper('B09D8BQM7C')
    # run_scraper('B09GB7Y272')