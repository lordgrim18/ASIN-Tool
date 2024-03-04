import hrequests
from price_parser import Price
import unicodedata

BASE_URL = 'https://www.amazon.in/dp/'

def scrape_data(asin: str):
    url = BASE_URL + asin
    session = hrequests.Session(browser='chrome')
    resp = session.get(url)
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


    page.close()

    return [product_name, discount, selling_price_value, max_retail_price, avg_rating, rating_count, product_specs]

    
if __name__ == '__main__':
    scraped_data = scrape_data(asin='B0BGS8PG3K')
    for data in scraped_data:
        print("\n", data)