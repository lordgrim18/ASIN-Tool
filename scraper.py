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

    # page.awaitSelector('input#filterByKeywordTextBox')
    # page.html.find('input#filterByKeywordTextBox').type(property)
    # page.html.find('input[aria-labelledby="a-autoid-2-announce"]').click()
    
    # page.awaitSelector('div[class="a-section review aok-relative"]')
    # reviews = page.html.find_all('div[class="a-section review aok-relative"]')
    # review_body = review.find('span[data-hook="review-body"]').text


    page.close()
    
if __name__ == '__main__':
    main()