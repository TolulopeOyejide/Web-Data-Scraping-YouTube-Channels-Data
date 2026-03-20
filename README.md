# YouTube Channel Data Scraper

A Python tool for collecting and exporting YouTube channel data using the **YouTube Data API v3** and **Selenium**. Extracts channel metrics into structured Excel output for analysis, competitive research, or reporting.

---

## Features

- Fetches channel-level data via the YouTube Data API v3
- Supports Selenium-based scraping for supplementary web data
- Exports clean, structured output to Excel (`.xlsx`)
- Modular `src/` codebase for easy extension

---

## Project Structure

```
Web-Data-Scraping-YouTube-Channels-Data/
├── src/                  # Source scripts
├── output/               # Generated Excel files
├── requirements.txt      # Python dependencies
└── README.md
```

---

## Prerequisites

- Python 3.8+
- A [Google Cloud](https://console.cloud.google.com/) project with the **YouTube Data API v3** enabled
- A valid **API key** from Google Cloud Console
- Google Chrome + matching [ChromeDriver](https://chromedriver.chromium.org/) (for Selenium)

---

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/TolulopeOyejide/Web-Data-Scraping-YouTube-Channels-Data.git
cd Web-Data-Scraping-YouTube-Channels-Data
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

**Dependencies:**

| Package | Purpose |
|---|---|
| `google-api-python-client` | YouTube Data API v3 integration |
| `selenium` | Browser automation / supplementary scraping |
| `pandas` | Data manipulation and transformation |
| `openpyxl` | Excel file export |

3. **Configure your API key**

Add your YouTube Data API key to the appropriate config variable in the source script (or via environment variable if supported):

```python
API_KEY = "YOUR_YOUTUBE_DATA_API_KEY"
```

> ⚠️ Never commit your API key to version control. Use environment variables or a `.env` file in production.

---

## Usage

Run the main scraper script from the `src/` directory:

```bash
python src/scraper.py
```

Results will be saved to the `output/` folder as an Excel file.

---

## Output

The exported `.xlsx` file contains structured channel data, which may include:

- Channel name and ID
- Subscriber count
- Total views
- Video count
- Channel description
- Custom URL / handle

---

## API Quota Note

The YouTube Data API v3 has a **daily quota limit** of 10,000 units by default. Batch requests and efficient querying are recommended for large-scale data collection. See [YouTube API Quota documentation](https://developers.google.com/youtube/v3/getting-started#quota) for details.

---

## License

This project is open source. Feel free to use and adapt with attribution.

---

## Author

**Tolulope Oyejide** — [InsightsVessel](https://github.com/TolulopeOyejide) | Senior ML Engineer & Data Professional
