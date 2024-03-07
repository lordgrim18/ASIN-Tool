import os
os.system("playwright install chromium")

import streamlit as st  
import pandas as pd
from time import sleep

from win10toast import ToastNotifier
toaster = ToastNotifier()

from scraper import run_scraper

st.title("ASIN Tool - Amazon Product Details Lookup")

st.markdown("""
Welcome to the ASIN Tool - your one-stop solution for fetching Amazon product details!

**Instructions:**
1. Enter the ASIN (Amazon Standard Identification Number) of the product you want to look up.
2. Click the "Search" button.
3. Wait for the data to be scraped from Amazon.

Once the data is fetched successfully, you'll be presented with detailed product information including its name, pricing, ratings, and specifications.

Let's get started!
""")

st.write(" ")
st.write(" ")

asin_input = st.text_input("Enter ASIN (Amazon Standard Identification Number):")

if st.button("Search"):
    if asin_input:
        with st.spinner("Scraping data from Amazon... Please wait."):
            run_scraper(asin_input)

        if os.path.exists('./data/product_data.csv'):
            toaster.show_toast("Data scraped successfully!", "Product data is available in the web app!", duration=5, threaded=True)
            st.write("### Product Data:")
            df = pd.read_csv('./data/product_data.csv')
            for data in df.values:
                st.write(f"**Product Name:** {data[0]}")
                st.write(f"**Discount:** {data[1]}%")
                st.write(f"**Selling Price:** {data[2]}")
                st.write(f"**Max Retail Price:** {data[3]}")
                st.write(f"**Average Rating:** {data[4]}")
                st.write(f"**Rating Count:** {data[5]}")
                st.write(f"**Product Specifications:**")
                for key, value in eval(data[6]).items():
                    st.write(f" - {key}: {value}")

            st.write(" ")
            st.write('### Want to download the data as a CSV file? Click the button below!')

            st.download_button(
            label="Download",
            data=df.to_csv(index=False),
            file_name='product_data.csv',
            mime='text/csv',
            )