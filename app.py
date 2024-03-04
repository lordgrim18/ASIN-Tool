import streamlit as st  

from scraper import scrape_data

st.title("ASIN Tool - Amazon Product Details Lookup")

asin_input = st.text_input("Enter ASIN (Amazon Standard Identification Number):")

if st.button("Search"):
    if asin_input:
        product_data = scrape_data(asin_input)
        if product_data:
            st.write("### Product Data:")
            st.write(f"**Product Name:** {product_data[0]}")
            st.write(f"**Discount:** {product_data[1]}%")
            st.write(f"**Selling Price:** ₹{product_data[2]}")
            st.write(f"**Max Retail Price:** ₹{product_data[3]}")
            st.write(f"**Average Rating:** {product_data[4]}")
            st.write(f"**Rating Count:** {product_data[5]}")
            st.write(f"**Product Specifications:**")
            for key, value in product_data[6].items():
                st.write(f"**{key}:** {value}")
        else:
            st.write("Product not found. Please check the ASIN.")