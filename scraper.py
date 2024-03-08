import asyncio
import unicodedata
import pandas as pd
from price_parser import Price
from playwright.async_api import async_playwright

BASE_URL = 'https://www.amazon.in/dp/'

async def get_product_name(page):
    """
    Asynchronous function to get the product name from the Amazon product page
    
    :param page: Playwright page object
    :return: product_name: str
    """
    try:
        await page.wait_for_selector('div#titleSection')
        product_name = await (await page.query_selector('div#titleSection')).text_content()
        product_name = product_name.strip()
    except Exception as e:
        # print('Error in finding product name:', e)
        product_name = 'Element not found'

    return product_name

async def get_product_price_discount(page):
    """
    Asynchronous function to get the product price, max retail price, currency used and discount from the Amazon product page
    Prices and discount is present in two different formats on Amazon product pages.
    This function tries to find the price and discount in both formats and returns the values, using try-except blocks.

    When no discount is available, and only the selling price is available, max retail price is also set to the selling price.
    Discount is calculated at the end as (MRP - Selling Price) / MRP * 100 if the selling price is available.
    
    :param page: Playwright page object
    :return: selling_price_value: float, max_retail_price: float, currency_used: str, discount: float

    """
    try:
        selling_price_element = await (await page.query_selector('span[class="a-price aok-align-center reinventPricePriceToPayMargin priceToPay"]')).text_content()
        selling_price_value = Price.fromstring(selling_price_element).amount_float

        currency_used = Price.fromstring(selling_price_element).currency

        max_retail_price_element = await (await page.query_selector('span[class="a-price a-text-price"]')).text_content()
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
    """
    Asynchronous function to get the average rating of the product from the Amazon product page.
    The average rating is present in the format '4.5 out of 5' on the Amazon product page.
    This function tries to find the average rating and returns the numerical value.

    :param page: Playwright page object
    :return: avg_rating: str
    """
    try:
        avg_rating = await (await page.query_selector('span[data-hook="rating-out-of-text"]')).text_content()
        avg_rating = avg_rating.strip().split(' ')[0]
    except Exception as e:
        # print('Error in finding average rating:', e)
        avg_rating = 'Not available'

    return avg_rating

async def get_rating_count(page):
    """
    Asynchronous function to get the total ratings of the product from the Amazon product page.
    The total ratings are present in the format '10,000 ratings' on the Amazon product page.
    This function tries to find the total ratings and returns the numerical value.

    :param page: Playwright page object
    :return: rating_count: str
    """
    try:
        rating_count = await (await page.query_selector('span[data-hook="total-review-count"]')).text_content()
        rating_count = rating_count.strip().split(' ')[0]
    except Exception as e:
        # print('Error in finding total ratings:', e)
        rating_count = 'Not available'

    return rating_count

async def get_product_specs(page):
    """
    Asynchronous function to get the product specifications from the Amazon product page.
    The product specifications are present in the format 'Key: Value' on the Amazon product page.
    Each key and value pair is extracted and stored in a dictionary.

    Product specifications are present in two different formats on Amazon product pages.
    This function tries to find the product specifications in both formats and returns the values, using try-except blocks.

    Sometimes, the product specifications also contains ASIN and Customer Reviews, 
    which are not required as we already have the ASIN and the ratings.

    The content is normalized to remove any special characters before storing it in the dictionary.

    :param page: Playwright page object
    :return: product_specs: dict
    """
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
                if key == 'Customer Reviews':
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
                if normalized_key == 'Customer Reviews':
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
    """
    Asynchronous function to scrape the product data from the Amazon product page using Playwright.

    Begins with creating a new playwright instance
    then a new browser is launched
    here we use chrome
    chrome for playwright is seperately installed using the command - 'python -m playwright install chromium'
    a new context is created for the browser
    a new page is created for the context.

    The page is navigated to the url of the product page using the ASIN
    The page is then waited for to load completely.
    Check is done to see if the ASIN is valid or not.
    This is done by checking if the page returns a product not found error,
    with the message 'The Web address you entered is not a functioning page on our site.'

    The product data includes the product name, price, discount, average rating, rating count and product specifications.
    The product data is stored in a pandas DataFrame and saved as a CSV file.

    :param asin: str
    """
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
    """
    Function to run the scraper asynchronously using the asyncio event loop.
    The asyncio event loop is set to ProactorEventLoop for Windows compatibility.
    The scraper is run using the run_until_complete method of the event loop.
    
    The scraper is run asynchronously using the asyncio event loop,
    so that it can be run in the background without blocking the main thread of the application, 
    which is the Streamlit web app.

    During deployment, the scraper is run using the asyncio directly,
    as the ProactorEventLoop is not required for deployment.

    :param asin: str
    """
    # loop = asyncio.ProactorEventLoop()
    # asyncio.set_event_loop(loop)
    # loop.run_until_complete(scrape_data(asin))

    asyncio.run(scrape_data(asin))

if __name__ == '__main__':

    # run_scraper('B08D8J88X3')
    # run_scraper('B09CKWH7W3')
    run_scraper('B0C9HXT93P')
    # run_scraper('B09D8BQM7C')
    # run_scraper('B09GB7Y272')