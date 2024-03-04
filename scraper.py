import hrequests

BASE_URL = 'https://www.amazon.in/dp/'

url = BASE_URL + 'B0BGS8PG3K'

def main():
    session = hrequests.Session(browser='chrome')
    resp = session.get(url)
    page = resp.render(mock_human=True)

    page.goto(url)

    page.awaitSelector('div#titleSection')
    product_name = page.html.find('div#titleSection').text.strip()  
    print(product_name)

    discount = page.html.find('span[class="a-size-large a-color-price savingPriceOverride aok-align-center reinventPriceSavingsPercentageMargin savingsPercentage"]').text.strip()
    print(discount)

    selling_price = page.html.find('span[class="a-price aok-align-center reinventPricePriceToPayMargin priceToPay"]')
    selling_price_value = selling_price.find('span[class="a-price-whole"]').text.strip()
    print(selling_price_value)

    avg_rating = page.html.find('span[data-hook="rating-out-of-text"]').text.strip()
    print(avg_rating)

    total_ratings = page.html.find('span[data-hook="total-review-count"]').text.strip()
    print(total_ratings)

    product_details = page.html.find('div#prodDetails')
    specs = product_details.find_all('table')
    for table in specs:
        for row in table.find_all('tr'):
            key = row.find('th').text.strip()
            value = row.find('td')
            if key == 'Customer Reviews':
                avg_rating_2 = value.find('a')
                avg_rating_2 = avg_rating_2.find('span').text.strip()
                rating_count = value.find('span#acrCustomerReviewText').text.strip()
                print(key, avg_rating_2, rating_count)
                continue
            print(key, value.text.strip())


    page.close()
    
if __name__ == '__main__':
    main()