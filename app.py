import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="Real Estate Price Analyzer", page_icon="🏠")

st.title("🏠 Real Estate Price Analyzer")
st.write("Predict House Prices using Machine Learning")

# Sample Dataset
data = {
    "area": [1000, 1200, 1500, 1800, 2000, 2200, 2500],
    "bedrooms": [2, 3, 3, 4, 4, 4, 5],
    "bathrooms": [1, 2, 2, 3, 3, 4, 4],
    "price": [5000000, 6500000, 7200000, 9000000, 10000000, 11500000, 13500000]
}

df = pd.DataFrame(data)

X = df[["area", "bedrooms", "bathrooms"]]
y = df["price"]

model = LinearRegression()
model.fit(X, y)

st.subheader("Enter Property Details")

area = st.number_input("Area (sq ft)", min_value=500, value=1200)
bedrooms = st.number_input("Bedrooms", min_value=1, value=2)
bathrooms = st.number_input("Bathrooms", min_value=1, value=1)

if st.button("Predict Price"):
    prediction = model.predict([[area, bedrooms, bathrooms]])
    
    st.success(f"🏠 Estimated House Price: ₹{int(prediction[0]):,}")

    st.subheader("Property Summary")
    st.write(f"📏 Area: {area} sq ft")
    st.write(f"🛏 Bedrooms: {bedrooms}")
    st.write(f"🚿 Bathrooms: {bathrooms}")
