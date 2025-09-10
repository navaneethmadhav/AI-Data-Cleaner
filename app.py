import os
import streamlit as st
import pandas as pd
import google.generativeai as genai
import io
from dotenv import load_dotenv

load_dotenv()
apiKey = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=apiKey)

st.title("Data Cleaner")
st.write("Upload a messy CSV/Excel file, and let us clean it for you!")

# File uploader
uploaded_file = st.file_uploader("Upload your file", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Read file
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.subheader("📊 Original Data")
    st.dataframe(df.head())

    def fix_spelling(text):
        if pd.isna(text):
            return text
        model = genai.GenerativeModel("gemini-pro")
        prompt = f"Correct spelling or standardize this value for data cleaning: '{text}'"
        response = model.generate_content(prompt)
        return response.text.strip()
    
    if 'object' in df.dtypes.values:
        if st.button("Clean Data"):
            cleaned_df = df.dropna()
        
            st.subheader("✨ Cleaned Data")
            st.dataframe(cleaned_df.head())

            towrite = io.BytesIO()
            cleaned_df.to_csv(towrite, index=False)
            towrite.seek(0)
            st.download_button(
                label="Download Cleaned CSV",
                data=towrite,
                file_name=f"{os.path.splitext(uploaded_file.name)[0]}_cleaned_data.csv",
                mime="text/csv"
            )
    else:
        option = st.selectbox("Clean Data By", ("Mean", "Median", "Drop"), index=None, placeholder="Select method...",)
    
        if option:
        
            st.write(f"Cleaning method selected: {option}")
            
            if option == "Drop":
                cleaned_df = df.dropna()
            
            elif option == "Median":
                cleaned_df = df.copy()

                for col in cleaned_df.columns:
                    if cleaned_df[col].dtype == "object":
                        # Fill missing with most frequent
                        cleaned_df[col].fillna(cleaned_df[col].mode()[0], inplace=True)
                        # Fix spelling errors
                        cleaned_df[col] = cleaned_df[col].apply(fix_spelling)
                    else:
                        # Fill missing numeric with median
                        cleaned_df[col].fillna(cleaned_df[col].median(), inplace=True)
                
            elif option == "Mean":
                cleaned_df = df.copy()
                
                for col in cleaned_df.columns:
                    if cleaned_df[col].dtype == "object":
                        cleaned_df[col].fillna(cleaned_df[col].mode()[0], inplace=True)
                        cleaned_df[col] = cleaned_df[col].apply(fix_spelling)
                    else:
                        # Fill missing numeric with mean
                        cleaned_df[col].fillna(cleaned_df[col].mean(), inplace=True)

            st.subheader("✨ Cleaned Data")
            st.dataframe(cleaned_df.head())

            towrite = io.BytesIO()
            cleaned_df.to_csv(towrite, index=False)
            towrite.seek(0)
            st.download_button(
                label="Download Cleaned CSV",
                data=towrite,
                file_name=f"{os.path.splitext(uploaded_file.name)[0]}_cleaned_data.csv",
                mime="text/csv"
            )