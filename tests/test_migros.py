# tests/test_migros.py
import unittest
from unittest.mock import patch
from stores.migros.migros_scraper import MigrosScraper

class TestMigrosScraper(unittest.TestCase):
    @patch('stores.migros.migros_scraper.SeleniumDriver')
    def test_scrape_and_parse(self, MockSeleniumDriver):
        # Mock Selenium behavior
        mock_driver = MockSeleniumDriver.return_value
        mock_driver.get_page_source.return_value = '<html>mocked HTML content</html>'

        # Initialize the scraper
        scraper = MigrosScraper()
        parsed_data = scraper.scrape_and_parse()

        # Assert the result
        self.assertIsInstance(parsed_data, list)
        scraper.close()

if __name__ == '__main__':
    unittest.main()
