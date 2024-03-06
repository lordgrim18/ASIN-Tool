import hrequests
from price_parser import Price
import unicodedata
import asyncio
import pandas as pd

BASE_URL = 'https://www.amazon.in/dp/'

async def scrape_data(asin: str):
    url = BASE_URL + asin
    # session = hrequests.Session(browser='chrome')
    # resp = session.get(url)
    # page = resp.render(mock_human=True)

    resp = hrequests.get(url)
    page = resp.render(mock_human=True)

    page.goto(url)

    page.awaitSelector('div#titleSection')
    product_name = page.html.find('div#titleSection').text.strip()  

    discount = page.html.find('span[class="a-size-large a-color-price savingPriceOverride aok-align-center reinventPriceSavingsPercentageMargin savingsPercentage"]').text.strip()
    discount = abs(int(discount[:-1]))

    selling_price = page.html.find('span[class="a-price aok-align-center reinventPricePriceToPayMargin priceToPay"]')
    selling_price_value = selling_price.find('span[class="a-price-whole"]').text.strip()
    selling_price_value = Price.fromstring(selling_price_value).amount_float

    max_retail_price = page.html.find('span[class="a-price a-text-price"]')
    max_retail_price = max_retail_price.find('span').text.strip()
    max_retail_price = Price.fromstring(max_retail_price).amount_float

    # avg_rating = page.html.find('span[data-hook="rating-out-of-text"]').text.strip()

    # total_ratings = page.html.find('span[data-hook="total-review-count"]').text.strip()

    product_specs = {}
    product_details = page.html.find('div#prodDetails')
    specs = product_details.find_all('table')

    for table in specs:
        for row in table.find_all('tr'):
            key = row.find('th').text.strip()
            value = row.find('td')
            if key == 'Customer Reviews':
                avg_rating = value.find('a')
                avg_rating = avg_rating.find('span').text.strip()
                rating_count = value.find('span#acrCustomerReviewText').text.strip()
                continue

            # Apply Unicode normalization
            normalized_value = unicodedata.normalize('NFD', value.text.strip()).encode('ascii', 'ignore').decode('utf-8')
            
            product_specs[key] = normalized_value

    df = pd.DataFrame()
    df['Product Name'] = [product_name]
    df['Discount'] = [discount]
    df['Selling Price'] = [selling_price_value]
    df['MRP'] = [max_retail_price]
    df['Average Rating'] = [avg_rating]
    df['Rating Count'] = [rating_count]
    df['Product Specs'] = [product_specs]

    df.to_csv('product_data.csv', index=False)


    page.close()

    print(product_name, discount, selling_price_value, max_retail_price, avg_rating, rating_count, product_specs)
    # return [product_name, discount, selling_price_value, max_retail_price, avg_rating, rating_count, product_specs]

def run_scraper(asin):
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(scrape_data(asin))
    
# if __name__ == '__main__':
#     # scraped_data = scrape_data(asin='B0BGS8PG3K')
#     # for data in scraped_data:
#     #     print("\n", data)

#     scraped_data = asyncio.run(scrape_data('B0BGS8PG3K'))
#     for data in scraped_data:
#         print("\n", data)

if __name__ == '__main__':
    # loop = asyncio.ProactorEventLoop()
    # asyncio.set_event_loop(loop)
    # loop.run_until_complete(single_category_scraper(keyword))
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(scrape_data('B0BGS8PG3K'))