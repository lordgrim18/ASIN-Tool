# Amazon ASIN Scraper

This project is a simple web application built with Streamlit that allows users to input Amazon ASIN (Amazon Standard Identification Number) and retrieve product details scraped from Amazon.

## Features

- User-friendly interface to enter ASIN.
- Scrapes essential product information from Amazon.
- Displays scraped data directly in the web app.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/lordgrim18/ASIN-Tool.git
    ```

2. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Install playwright dependencies:

   ```bash
   playwright install chromium
   ```

## Usage

1. Run the Streamlit app:

   ```bash
   streamlit run app.py
   ```

2. Open the provided URL in your web browser:

   Local URL: `http://localhost:8501`

3. Enter an ASIN in the text input field and click "Search".

4. The scraped product details will be displayed below.
