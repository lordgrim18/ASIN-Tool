import hrequests

BASE_URL = 'https://www.amazon.in/dp/'

url = BASE_URL + 'B07XVMDRZY'

def main():
    session = hrequests.Session(browser='chrome')
    resp = session.get(url)
    page = resp.render(mock_human=True)

    page.close()
    
if __name__ == '__main__':
    main()