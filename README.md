# Vegetable Scraper Project

## Project Overview

This project is a Python-based web scraper that extracts vegetable data (such as prices, availability, and names) from three major Swiss supermarket websites: Migros, Aldi, and Denner. The scraper uses Selenium for interacting with the web pages and extracting the required data. The project is divided into three separate scrapers, one for each supermarket, with common utilities shared between them to ensure maintainability and code reuse.

### Features

- **Store-Specific Scrapers**: Each scraper is tailored to the specific structure of the Migros, Aldi, and Denner websites.
- **Data Parsing**: Extracted HTML is parsed and cleaned to produce structured data (e.g., JSON or CSV) for further use.
- **Modular Design**: Each store scraper is a standalone module with shared utilities for common tasks.
- **Error Handling & Logging**: Robust error handling and logging ensure reliability in case of website structure changes or network issues.
- **Automated Testing**: Unit tests are in place for each store scraper to verify the functionality.

---

## Project Structure

```bash
.
├── README.md
├── requirements.txt
├── config/
│   ├── migros_config.py
│   ├── aldi_config.py
│   ├── denner_config.py
├── stores/
│   ├── migros/
│   │   ├── migros_scraper.py
│   │   ├── migros_parser.py
│   ├── aldi/
│   │   ├── aldi_scraper.py
│   │   ├── aldi_parser.py
│   ├── denner/
│   │   ├── denner_scraper.py
│   │   ├── denner_parser.py
├── common/
│   ├── selenium_utils.py
│   ├── parser_utils.py
│   ├── data_cleaner.py
├── main.py
└── tests/
    ├── test_migros.py
    ├── test_aldi.py
    ├── test_denner.py
