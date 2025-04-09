# Real-Time-API-Manufacturer-Discovery-using-AI-Agents

This Streamlit-based application allows users to search for pharmaceutical API manufacturers worldwide by entering an API name and a country. It fetches and displays results from an existing PostgreSQL dataset and also scrapes additional data from the web to ensure comprehensive and up-to-date manufacturer information.

---

## Features -

- Search by API and Country : Enter any API name and country to get relevant manufacturer details.
- LLM-Powered Scraping : If existing data is outdated or missing, the tool uses a large language model pipeline to scrape fresh data from pharmaceutical directories and websites.
- PostgreSQL Integration : Efficiently fetches data from a PostgreSQL database, avoiding redundant scraping.
- Deduplication Logic : Ensures the results are unique, even when new data is appended.
- Validation Check : Ensures the manufacturer listed actually produces the queried API.
- Tabular Display : Neatly displays the results with columns: `apiname`, `manufacturers`, `country`, `usdmf`, `cep`.

---

## Working -

### 1.User Input Phase :
- The user is prompted to enter two fields:
  - **API Name** (e.g., `lenalidomide`)
  - **Country** (e.g., `usa`)
- On clicking the **Search & Scrape** button, the front end sends these values to the backend to initiate the data lookup process.

### 2.Initial Database Query :
- The backend first checks the **PostgreSQL** database to see if relevant data already exists.
- If a matching entry is found:
  - The result is fetched instantly and shown in a stylized table.
  - A green success message appears: `Data retrieved from PostgreSQL.`
- This step avoids unnecessary scraping and speeds up the result display.

### 3.LLM-Supported Scraping Trigger (Conditional) :
- If no result is found or data is deemed **outdated**, the tool triggers a scraping pipeline.
- This process is powered by an LLM agent (Qwen-2.5-32B via Agno), capable of intelligent searching and interpretation.
- Scraping occurs across trusted pharma sources such as:
  - FDA Orange Book (regulatory data)
  - Pharmaoffer (B2B API directories)
  - Pharmacompass (manufacturer listings)
  - and many more.

### 4.Cleaning, Comparison, and Deduplication :
- Scraped data undergoes cleansing and transformation.
- Existing PostgreSQL records are cross-checked to avoid duplication.
- Only new, non-overlapping manufacturer entries are inserted into the database.

### 5.Manufacturer Verification Using NLP :
- The model performs semantic analysis using NLP techniques.
- It confirms whether a company truly manufactures the given API:
  - Distributor mentions are filtered out.
  - Only companies with confirmed production capabilities are accepted.

### 6.Unified Display Output :
- Final result shown to the user is a **merged view** from:
  - Existing PostgreSQL data
  - Newly validated scrape entries (if any)
- Output columns include:
  - `apiname`, `manufacturers`, `country`, `usdmf`, `cep`
- The structured, tabular format allows **quick decision-making** for industry professionals.

### 7. 📊 Frontend Feedback
- PostgreSQL-sourced results trigger a green badge.
- If scraping takes longer, users can infer it from latency before results appear.
- All output is shown in a well-formatted interactive table.

---
 Tech Stack :

- Frontend : Streamlit (with styled UI and status indicators)
- Backend : Python
- LLM Agent : Groq's Qwen-2.5-32B via Agno's agent framework
- Web Scraping : DuckDuckGo, Crawl4AI, FDA Orange Book, Pharmaoffer, Pharmacompass
- Database : PostgreSQL

---

## Setup Instructions :

1. Clone this repository:
```bash
git clone https://github.com/your-username/api-manufacturer-lookup.git
cd api-manufacturer-lookup
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up PostgreSQL and provide credentials in `.env` or config.

4. Launch the Streamlit app:
```bash
streamlit run app.py
```

---

- The scraping pipeline runs only when required to avoid overuse of resources.
- PostgreSQL acts as the central storage and cache.
- All displayed manufacturer data is validated and de-duplicated.
- Supports certification filters (e.g., USDMF and CEP) to ensure regulatory compliance.

---

Example Use Case

- Input : API = `lenalidomide`, Country = `usa`
- Output :
   - Data retrieved from PostgreSQL:
     | apiname       | manufacturers            | country | usdmf | cep  |
     |---------------|---------------------------|---------|-------|------|
     | lenalidomide | Advinus Therapeutics     | usa     | Yes   | Yes  |
     | lenalidomide | Celgene Corporation      | usa     | Yes   | Yes  |
     | lenalidomide | Dr. Reddy's Laboratories | usa     | Yes   | No   |
     | lenalidomide | Hetero USA Inc.          | usa     | Yes   | Yes  |
     | lenalidomide | Mylan N.V.               | usa     | Yes   | Yes  |

---

Domain Relevance

This tool is highly relevant for:
- Pharmaceutical supply chain analysts
- Regulatory affairs professionals
- API procurement specialists

Use cases include supplier qualification, USDMF/CEP verification, and competitive intelligence in the API landscape.



