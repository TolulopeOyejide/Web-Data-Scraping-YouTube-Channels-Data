# Web Data Scraping: YouTube Channels Data
This repository contains a Python-based solution for scraping public data from YouTube channels. It is designed to extract video metadata, including titles, view counts and upload timing, to support data analysis and content strategy research.


## Features
- **Automated Extraction:** Scrapes video titles, views, and duration/upload status.

- **Dynamic Content Handling:** Uses Selenium to manage YouTube's infinite scroll and dynamic loading.

- **Structured Output:** Exports collected data directly into CSV format for analysis in Excel or Pandas.
  

## Prerequisites
Before running the scraper, ensure you have Python 3.x installed along with the following dependencies:

- `selenium`:For browser automation.

- `beautifulsoup4`: For HTML parsing.

- `pandas`: For data structuring and CSV export.

- `webdriver-manager`: To automatically handle Chromium/ChromeDriver setup.


## Installation
1. Clone the repository:
`git clone https://github.com/TolulopeOyejide/Web-Data-Scraping-YouTube-Channels-Data.git`

2. Navigate to the project directory:
`cd Web-Data-Scraping-YouTube-Channels-Data`

3. Install dependencies:
`pip install -r requirements.txt`
