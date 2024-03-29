## command to be used during deployment for installing playwright dependency
import os
os.system("playwright install chromium")

# importing libraries
import pandas as pd
import streamlit as st

from scraper import run_scraper

# creating an instance of the ToastNotifier class to display notifications

# setting the title of the web app
st.title("ASIN Tool - Amazon Product Details Lookup")

# setting the description of the web app
st.markdown("""
Welcome to the ASIN Tool - your one-stop solution for fetching Amazon product details!

**Instructions:**
1. Enter the ASIN (Amazon Standard Identification Number) of the product you want to look up.
2. Click the "Search" button.
3. Wait for the data to be scraped from Amazon.

Once the data is fetched successfully, you'll be presented with detailed product information including its name, pricing, ratings, and specifications.

Let's get started!
""")

# Expander for ASIN intro
with st.expander("What is an ASIN?"):
    st.markdown("""
    ASIN stands for **Amazon Standard Identification Number**. It's a unique alphanumeric code assigned to each product on Amazon. Every ASIN will be 10 digits and consist of a combination of letters and digits.

    You can find the ASIN of a product on its product page, usually located in the product details section. 
    Or you can get it from the url of the Product Description Page. 

    Knowing the ASIN allows you to quickly look up specific product details on Amazon or use tools like this one to scrape data about the product.
    """)

st.write(" ")
st.write(" ")

# setting the session state for displaying the data
if 'display_data_bool' not in st.session_state:
    st.session_state.display_data_bool = False

# text input for ASIN
asin_input = st.text_input("Enter ASIN (Amazon Standard Identification Number):")

if st.button("Search"):
  st.session_state.display_data_bool = False
  if asin_input:
    if os.path.exists('./data/product_data.csv'):
        check_df = pd.read_csv('./data/product_data.csv')
        if check_df['ASIN'][0] == asin_input:
          st.session_state.display_data_bool = True
        #   Notification("Data already present!", "Product data is available in the web app!", icon="info").show()
          st.rerun()
    with st.spinner("Scraping data from Amazon... Please wait."):
        run_scraper(asin_input)
        st.session_state.display_data_bool = True

    if os.path.exists('./data/product_data.csv'):
        check_df = pd.read_csv('./data/product_data.csv')
        if check_df['ASIN'][0] == 'Invalid ASIN':
          st.error("Invalid ASIN entered. Please try again.")
        #   Notification("Invalid ASIN entered!", "Please enter a valid ASIN.", icon="error").show()
          st.session_state.display_data_bool = False

# displaying the data
if st.session_state.display_data_bool:
    st.write("### Product Data:")
    df = pd.read_csv('./data/product_data.csv')
    for data in df.values:
        st.write(f"**ASIN:** {data[0]}")
        st.write(f"**Product Name:** {data[1]}")
        if data[2] == data[3] == data[4] == 'Not available':
            st.write(f"**Currently unavailable**")
            st.write(f"No price and discount present")
            st.write(" ")
        else:
            st.write(f"**Discount:** {data[2]}")
            st.write(f"**Selling Price:** {data[3]}")
            st.write(f"**Max Retail Price:** {data[4]}")
            st.write(f"**Currency:** {data[5]}")
        st.write(f"**Average Rating:** {data[6]}")
        st.write(f"**Rating Count:** {data[7]}")
        st.write(f"**Product Specifications:**")
        if data[8] == 'Not available':
            st.write(" - Not available")
        else:
            for key, value in eval(data[8]).items():
                st.write(f" - {key}: {value}")

    st.write(" ")

    st.write('### Want to download the data as a CSV file? Click the button below!')

    # setting the data to be downloaded
    df_to_download = df.copy()
    product_specs = df_to_download['product_specs'][0]
    product_specs = product_specs.replace('{', '').replace('}', '').replace("'", '').split(', ')
    product_specs = '\n'.join(product_specs)
    df_to_download['product_specs'] = product_specs

    # download button
    st.download_button(
    label="Download",
    data=df_to_download.to_csv(index=False),
    file_name='product_data.csv',
    mime='text/csv',
    )