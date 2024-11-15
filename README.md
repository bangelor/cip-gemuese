
# Store Price Scraper in Switzerland: ***An adventurous scout through fruits and vegetables***  🍌

Mirror, mirror on the wall, who has the cheapest banana of them all? We've asked ourselves this question too. We live in the age of information, and therefore, a fair and timely comparison of groceries based on the published data on retailers' websites should be possible. 

## Goal 🎯
We aim to close this transparency gap by a well-designed web crawling system. This project aims to compare the prices, quality, and ecological aspects of fruits and vegetables sold by major retailers in Switzerland. We focus on the food category of "fruits and vegetables," as these products are often discussed controversially due to their social, ecological, and societal implications

## Retailers 🏬
For data collection and analysis, we have taken the following retailers into account.

- [Migros](https://www.migros.ch/de)
- [Aldi](https://www.aldi-now.ch/de)
- [Lidl](https://sortiment.lidl.ch/de)

## Project Structure 🗂️
```
├── analysis/                         # Merged data stage for analyzing
│   ├── merge_files_jupyer.ipynb      # Integration and processing of scraped and cleanded files of retailers
│   ├── analysis.ipynb                # Answering research questions
├── stores/                           # Store-specific scrapers and parsers
│   ├── migros/                       # Migros scraping module
│   │   ├── migros_scraper.py         # Scraper for Migros
│   │   ├── migros_parser.py          # Parser for Migros HTML content
│   ├── lidl/                         # Lild scraping and transformation scripts
│   │   ├── lidl_scraper.py           # Scraper and parser for Lidl
│   │   ├── lidl_transform.py         # Transformation and cleaning scraped data for analytics purpose
│   ├── aldi/                         # Aldi scraping and transformation scripts
│   │   ├── aldi scraper.py           # Scraper and parser for Aldi (with Selenium)
│   │   ├── aldi_parser_improved.py   # Scraper and parser for Aldi (without Selenium)
│   │   ├── csv_cleaner.py            # Transformation and cleaning scraped data for analytics purpose
├── README.md                         # Project documentation
├── requirements.txt                  # Python dependencies

```
## Approach 💡
- Every store has its own scraper, parser and cleaner files. For setting up the Migros stores, which is structured in a highly modular, scalable and object-oriented manner, please refer to the README.md in the respective folder. 
- The cleaned and transformed datasets for each retailer are integrated and refined in the file ***merge_files_jupyter.ipynb*** so that they can subsequently be analyzed using the file ***analysis.ipynb***. For data cleansing in the merged data stage, it must be ensured that the corresponding datasets are correctly stored in the respective folders.

```
├── migros ├── migros_scraper_parser_2024-11-11-Nov-19.csv  ──
                                                              ──
                                                                ──
├── lidl   ├── lidl_transform.csv  ── ── ── ── ── ── ── ── ── ── ──   merge_files_jupyter.ipynb ─── ──> stores_combined_all.csv ─── ──> analysis.ipynb
                                                               ──
                                                            ──
├── aldi   ├── aldi_transform.csv                         ──

```

### License ⚖️

This project is licensed under the MIT License. See the `LICENSE` file for more information.

### Contact ❓

If you have any questions or need further assistance, feel free to reach out:

- Email: lorenz.bangerter@icloud.com
- GitHub: [bangelor](https://github.com/bangelor)
