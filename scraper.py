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
        except Exception as e:
            print('Error in finding product name:', e)
            product_name = 'Element not found'

        print(product_name)

        try:
            discount_element = await page.query_selector('span[class="a-size-large a-color-price savingPriceOverride aok-align-center reinventPriceSavingsPercentageMargin savingsPercentage"]')
            discount = await discount_element.text_content()
            discount = abs(int(discount[:-1]))
        except Exception as e:
            print('No discount', e)
            discount = 0

        print(discount)

        try:
            selling_price_element = await (await page.query_selector('span[class="a-price aok-align-center reinventPricePriceToPayMargin priceToPay"]')).text_content()
            selling_price_value = Price.fromstring(selling_price_element).amount_float
            currency_used = Price.fromstring(selling_price_element).currency
        except Exception as e:
            print('Error in finding selling price:' ,e)
            selling_price_value = 'Not available'

        print(selling_price_value)

        try:
            max_retail_price_element = await (await page.query_selector('span[class="a-price a-text-price"]')).text_content()
            # max_retail_price = await max_retail_price_element.query_selector('span').text_content()
            max_retail_price = Price.fromstring(max_retail_price_element).amount_float
        except Exception as e:
            print('Error in finding max retail price:', e)
            max_retail_price = 'Not available'

        print(max_retail_price)

        try:
            avg_rating = await (await page.query_selector('span[data-hook="rating-out-of-text"]')).text_content()
            avg_rating = avg_rating.strip()
            avg_rating = avg_rating.split(' ')[0]
        except Exception as e:
            print('Error in finding average rating:', e)
            avg_rating = 'Not available'
        
        print(avg_rating)

        try:
            rating_count = await (await page.query_selector('span[data-hook="total-review-count"]')).text_content()
            rating_count = rating_count.strip()
            rating_count = rating_count.split(' ')[0]
        except Exception as e:
            print('Error in finding total ratings:', e)
            rating_count = 'Not available'

        print(rating_count)

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
                print('Error in finding specifications:', e)
                product_specs = 'Not available'

        print(product_specs)

        await browser.close()

    df = pd.DataFrame()
    df['ASIN'] = [asin]
    df['product_name'] = [product_name]
    df['discount'] = [discount]
    df['selling_price'] = [selling_price_value]
    df['MRP'] = [max_retail_price]
    df['currency_used'] = [currency_used]
    df['average_rating'] = [avg_rating]
    df['rating_count'] = [rating_count]
    df['product_specs'] = [product_specs]

    df.to_csv('./data/product_data.csv', index=False)


def run_scraper(asin: str):
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(scrape_data(asin))

    # asyncio.run(scrape_data(asin))

if __name__ == '__main__':

    # run_scraper('B0BGS8PG3K')
    run_scraper('B083FQS2GZ')