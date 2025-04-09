import streamlit as st
import subprocess
import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# PostgreSQL credentials
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_PORT = os.getenv("DB_PORT", "5432")

# Set page config
st.set_page_config(
    page_title="API Manufacturer Lookup",
    page_icon="🧬",
    layout="centered"
)

# === Load background image ===
def set_background(image_path):
    with open(image_path, "rb") as f:
        img_bytes = f.read()
    b64_encoded = base64.b64encode(img_bytes).decode()
    bg_img_css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{b64_encoded}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        color: black !important;
    }}
    .stTextInput > div > div > input {{
        background-color: #ffffffaa;
        color: #000000;
        border: 1px solid #ccc;
        border-radius: 5px;
    }}
    .stButton > button {{
        background-color: #0a9396;
        color: white;
        font-weight: bold;
        border-radius: 5px;
    }}
    .stDataFrame {{
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 10px;
        padding: 10px;
    }}
    </style>
    """
    st.markdown(bg_img_css, unsafe_allow_html=True)

import base64
set_background("/Users/prabhas/Desktop/pharmacompass/prabhas.jpg")  # Make sure this image is in the same folder

# === Title Section ===
st.markdown("<h1 style='text-align:center; color:#001f54;'>🌐 API Manufacturer Lookup</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:18px; color:#002b5b;'>Search global pharmaceutical API manufacturers and USDMF/CEP certifications.</p>", unsafe_allow_html=True)

# === Input Section ===
st.markdown("### 🔎 Search Parameters")
api_name = st.text_input("Enter API Name")
country = st.text_input("Enter Country")

# === Button & Backend Trigger ===
if st.button("🔍 Search & Scrape"):
    if api_name and country:
        with st.spinner("Running scraper, please wait..."):
            subprocess.run(["python", "new5.py", api_name, country])

        try:
            conn = psycopg2.connect(
                dbname=DB_NAME, user=DB_USER, password=DB_PASS,
                host=DB_HOST, port=DB_PORT
            )
            query = """
            SELECT apiname, manufacturers, country, usdmf, cep 
            FROM manufacturers 
            WHERE apiname = %s AND country = %s;
            """
            df = pd.read_sql(query, conn, params=(api_name.lower(), country.lower()))
            conn.close()

            if df.empty:
                st.warning("No data found in database.")
            else:
                st.success("Data fetched from PostgreSQL.")
                st.dataframe(df)
        except Exception as e:
            st.error(f"Database error: {e}")
    else:
        st.warning("Please fill in both API Name and Country.")
