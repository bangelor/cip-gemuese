
# Store Price Scraper

This project is a modular, object-oriented Python application that scrapes product prices from different stores and uploads the scraped data to Azure Blob Storage. Each store has its own scraper and parser, making it easy to extend the application to scrape from additional stores in the future.

## Project Structure

```
.
├── README.md                 # Project documentation
├── requirements.txt          # Python dependencies
├── config/                   # Configuration files
│   ├── azure_config.py       # Azure storage connection details
│   ├── migros_config.py      # Migros-specific config
├── stores/                   # Store-specific scrapers and parsers
│   ├── migros/               # Migros scraping module
│   │   ├── migros_scraper.py # Scraper for Migros
│   │   ├── migros_parser.py  # Parser for Migros HTML content
│   ├── aldi/                 # Aldi scraping module
│   ├── denner/               # Denner scraping module
├── common/                   # Common utilities
│   ├── selenium_utils.py     # Utilities for Selenium-based scraping
│   ├── data_cleaner.py       # Shared data cleaning utilities
├── storage/                  # Storage modules
│   ├── azure_blob_storage.py # Azure Blob Storage upload functionality
├── main.py                   # Main entry point to run the scraper
└── tests/                    # Unit tests
    ├── test_migros.py        # Tests for the Migros scraper
```

## Features

- **Modular Design**: Each store has its own scraper and parser, making it easy to add more stores.
- **Configurable**: Connection details and other configurations are stored in separate files under the `config/` directory.
- **Cloud Storage**: Scraped data is uploaded to Azure Blob Storage.
- **Schedule Support**: The app can be scheduled to run at specific intervals using `cron`, `schedule` module, or cloud services.

## Getting Started

### Prerequisites

Make sure you have the following installed:

- **Python 3.8+**
- **pip** (Python package manager)
- **Chrome Browser** (if using Selenium with Chrome)
- **ChromeDriver** (Automatically handled by the `webdriver_manager` package)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/store-price-scraper.git
   cd store-price-scraper
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up Azure Blob Storage connection:

   Create a `config/azure_config.py` file with your Azure Blob Storage connection details:

   ```python
   AZURE_CONNECTION_STRING = 'your_azure_blob_connection_string'
   AZURE_CONTAINER_NAME = 'your_container_name'
   ```

   Alternatively, set environment variables:

   ```bash
   export AZURE_CONNECTION_STRING='your_actual_connection_string'
   export AZURE_CONTAINER_NAME='your_container_name'
   ```

### Running the Scraper

You can run the scraper for Migros by executing:

```bash
python main.py
```

This will scrape product data from Migros and upload it to Azure Blob Storage.

### Developer Onboarding

#### 1. **Understanding the Project**

- Each store has its own folder inside `stores/` (e.g., `migros`, `aldi`, `denner`). These folders contain:
  - `scraper.py`: Scrapes the store website using Selenium.
  - `parser.py`: Parses the scraped HTML data into a structured format.
  
- Common utilities such as Selenium utilities, data cleaners, and storage modules are stored in the `common/` and `storage/` directories.

#### 2. **Adding a New Store**

To add a new store, follow these steps:
1. Create a new folder for the store under `stores/`, e.g., `stores/new_store/`.
2. Inside this folder, create:
   - `new_store_scraper.py` for scraping logic.
   - `new_store_parser.py` for parsing the scraped HTML.
3. Update `main.py` to integrate the new scraper.

#### 3. **Running Unit Tests**

Unit tests are located in the `tests/` directory. You can run the tests using `unittest`:

```bash
python -m unittest discover tests/
```

#### 4. **Scheduling the Scraper**

You can schedule the scraper to run at regular intervals:

- **Using Python’s `schedule` module**: Already integrated in `main.py` for scheduling jobs.
- **Using `cron` (Linux/MacOS)**:
  
  Open `crontab`:

  ```bash
  crontab -e
  ```

  Add the following line to schedule the scraper to run daily at midnight:

  ```bash
  0 0 * * * /usr/bin/python3 /path/to/project/main.py
  ```

- **Using Task Scheduler (Windows)**: Use Windows Task Scheduler to trigger `main.py` at desired intervals.

### Contributing

1. Fork the repo and create your branch from `main`.
2. Make your changes, ensuring that your code is well-structured and documented.
3. Write tests for any new functionality.
4. Submit a pull request!

### License

This project is licensed under the MIT License. See the `LICENSE` file for more information.

### Contact

If you have any questions or need further assistance, feel free to reach out:

- Email: lorenz.bangerter@icloud.com
- GitHub: [bangelor](https://github.com/bangelor)
