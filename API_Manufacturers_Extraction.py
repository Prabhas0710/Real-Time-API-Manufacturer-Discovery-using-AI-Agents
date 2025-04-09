import pandas as pd
import os
import time
import psycopg2
import sys
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools
from phi.tools.crawl4ai_tools import Crawl4aiTools

# === Load environment variables ===
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# PostgreSQL Credentials
DB_HOST = os.getenv("DB_HOST", "13.201.178.49")
DB_NAME = os.getenv("DB_NAME", "ps_large")
DB_USER = os.getenv("DB_USER", "ps_user")
DB_PASS = os.getenv("DB_PASS", "cccVNjDkj")
DB_PORT = os.getenv("DB_PORT", "5432")

# === Read Command-line Arguments or Streamlit Input ===
if len(sys.argv) < 3:
    print("Usage: python new5.py <api_name> <country>")
    sys.exit(1)

api_name = sys.argv[1].strip().lower()
country_input = sys.argv[2].strip().lower()

print(f"🔍 Looking up: API = '{api_name}' | Country = '{country_input}'")

# === Load CSV Dataset ===
try:
    df = pd.read_csv("/Users/prabhas/Desktop/prabhas5.csv", encoding='latin1')
    df['apiname'] = df['apiname'].str.strip().str.lower()
    df['country'] = df['country'].str.strip().str.lower()
except Exception as e:
    print(f"⚠️ CSV Load Failed: {e}")
    df = pd.DataFrame(columns=['apiname', 'manufacturers', 'country', 'usdmf', 'cep'])

# === Check for Existing Manufacturers in CSV ===
existing_df = df[
    (df['apiname'].str.contains(api_name, na=False)) &
    (df['country'].str.contains(country_input, na=False))
]

# === Collect Skip List from CSV ===
existing_manufacturers = set(existing_df['manufacturers'].dropna().str.strip().str.lower().unique())

# === Helper: Extract Manufacturer Info from Markdown ===
def extract_manufacturers(markdown_output):
    manufacturers = []
    if not markdown_output:
        return manufacturers

    lines = markdown_output.splitlines()
    for line in lines:
        if "|" in line and not line.lower().startswith("| manufacturers") and not line.startswith("|---"):
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 4:
                manu_name = parts[0]
                country = parts[1].lower()
                usdmf_status = 'Yes' if parts[2].strip().lower() in ['yes', 't'] else 'No'
                cep_status = 'Yes' if parts[3].strip().lower() in ['yes', 't'] else 'No'

                if manu_name.lower() not in existing_manufacturers and (country_input in country):
                    manufacturers.append({
                        'apiname': api_name,
                        'manufacturers': manu_name,
                        'country': country,
                        'usdmf': usdmf_status,
                        'cep': cep_status
                    })
    return manufacturers

# === Agent Factories ===
def create_web_agent(skip_list):
    return Agent(
        name="Web Agent",
        role="Find fresh API manufacturer data from reputable sources.",
        model=Groq(id="qwen-2.5-32b"),
        tools=[DuckDuckGoTools()],
        instructions=f"""
            Search FDA Orange Book, Pharmaoffer, Pharmacompass for manufacturers of {api_name} API in {country_input}.
            Skip known manufacturers: {', '.join(skip_list)}.
            Output strictly as a Markdown table:
            | manufacturers | country | usdmf | cep |
            |----------------|---------|------|------|
        """,
        show_tool_calls=True,
        markdown=True,
    )

def create_pharma_agent(skip_list):
    return Agent(
        name="Pharma Agent",
        role="Crawl pharma directories & FDA Orange Book for new manufacturers of API.",
        model=Groq(id="qwen-2.5-32b"),
        tools=[Crawl4aiTools()],
        instructions=f"""
            Crawl FDA Orange Book and pharma directories for {api_name} API in {country_input}.
            Skip known manufacturers: {', '.join(skip_list)}.
            Output strictly in Markdown table:
            | manufacturers | country | usdmf | cep |
            |----------------|---------|------|------|
        """,
        show_tool_calls=True,
        markdown=True,
    )

# === Main Scraping Logic ===
batch_size = 30
existing_manufacturer_list = sorted(existing_manufacturers)
web_manufacturer_rows = []
pharma_rows = []

# 🟡 Run Scraper Regardless of Existing Data
batches = [existing_manufacturer_list[i:i + batch_size] for i in range(0, len(existing_manufacturer_list), batch_size)] or [[]]

for skip_batch in batches:
    try:
        web_agent = create_web_agent(skip_batch)
        web_result = web_agent.run(f"Find {api_name} API manufacturers in {country_input}.")
        if web_result:
            web_manufacturer_rows.extend(extract_manufacturers(web_result.content))
        time.sleep(2)
    except Exception as e:
        print(f"⚠️ Web Agent failed: {e}")

    try:
        pharma_agent = create_pharma_agent(skip_batch)
        pharma_result = pharma_agent.run(f"Crawl for {api_name} API manufacturers in {country_input}.")
        if pharma_result:
            pharma_rows.extend(extract_manufacturers(pharma_result.content))
        time.sleep(2)
    except Exception as e:
        print(f"⚠️ Pharma Agent failed: {e}")

# === Check for Total Rows ===
combined_scraped_rows = web_manufacturer_rows + pharma_rows
if not combined_scraped_rows:
    print(f"❌ No API manufacturers found for '{api_name}' in '{country_input}'.")
    sys.exit(0)

# === Insert into PostgreSQL ===
def insert_into_postgres(existing_df, fresh_df):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()

        combined_df = pd.concat([existing_df, fresh_df], ignore_index=True).drop_duplicates()
        insert_query = """
        INSERT INTO manufacturers (apiname, manufacturers, country, usdmf, cep)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (apiname,manufacturers, country) DO NOTHING;
        """

        for _, row in combined_df.iterrows():
            cursor.execute(insert_query, (row['apiname'], row['manufacturers'], row['country'], row['usdmf'], row['cep']))

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Data inserted into PostgreSQL successfully!")
    except Exception as e:
        print(f"❌ Error inserting into PostgreSQL: {e}")

# === Final Insert ===
fresh_df = pd.DataFrame(combined_scraped_rows)
insert_into_postgres(existing_df, fresh_df)
