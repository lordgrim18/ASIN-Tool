import os
os.system("playwright install chromium")

import streamlit as st  
import pandas as pd

from scraper import run_scraper, scrape_data

def main():

    st.title("ASIN Tool - Amazon Product Details Lookup")

    asin_input = st.text_input("Enter ASIN (Amazon Standard Identification Number):")

    if st.button("Search"):
        if asin_input:

            # run_scraper(asin_input)
            if os.path.exists('product_data.csv'):
                st.write("### Product Data:")
                df = pd.read_csv('product_data.csv')
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


if __name__ == "__main__":
    main()