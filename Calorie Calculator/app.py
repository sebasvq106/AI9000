import streamlit as st
from calorie_calculator import analyze_image_macros
import matplotlib.pyplot as plt

st.set_page_config(page_title="Food Macro Analyzer", layout="centered")

st.title("🍱 Food Macro Analyzer")
st.write("Upload a picture of your meal and get the macronutrients.")

uploaded_file = st.file_uploader("Upload food image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.image(uploaded_file, width="stretch")

    if st.button("🔍 Analyze food"):
        with st.spinner("Analyzing with AI..."):
            result = analyze_image_macros(uploaded_file.read())
            caption = result["caption"]
            ingredients = result["ingredients"]

        st.success("Analysis complete!")

        # Show Caption
        st.subheader("🧠 AI Caption")
        st.info(caption)

        # Show Macros
        st.subheader("📊 Macros")
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Calories", f"{result['calories']:.1f} kcal")
        col2.metric("Protein", f'{result["protein"]:.1f} g')
        col3.metric("Carbs", f'{result["carbs"]:.1f} g')
        col4.metric("Fat", f'{result["fat"]:.1f} g')

        # Show ingredients
        st.subheader("🥗 Ingredients detected")

        for ing in ingredients:
            st.write(f"• {ing['name']} — {ing['grams']} g")

        # Show Graph
        st.subheader("📈 Distribution")

        labels = ["Protein", "Carbs", "Fat"]
        values = [
            result["protein"],
            result["carbs"],
            result["fat"],
        ]

        fig, ax = plt.subplots()
        ax.barh(labels, values)
        ax.set_xlabel("Grams")

        st.pyplot(fig)
