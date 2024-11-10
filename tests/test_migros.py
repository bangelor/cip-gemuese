### Produced by ChatGPT and not tested :D
import unittest
from unittest.mock import patch, MagicMock
from stores.migros.migros_scraper import MigrosScraper
from stores.migros.migros_parser import MigrosParser

class TestMigrosScraper(unittest.TestCase):
    
    @patch('stores.migros.migros_scraper.SeleniumDriver')
    def test_scrape_and_parse(self, MockSeleniumDriver):
        """Test that the scrape and parse method works as expected."""
        # Mocking the SeleniumDriver and its methods
        mock_driver = MockSeleniumDriver.return_value
        mock_driver.get_page_source.return_value = """
        <html>
            <article class="product-card">
                <span data-cy="product-name-123">Test Product 1</span>
                <span data-cy="current-price">10.00</span>
            </article>
            <article class="product-card">
                <span data-cy="product-name-456">Test Product 2</span>
                <span data-cy="current-price">20.00</span>
            </article>
        </html>
        """
        
        # Instantiate the scraper
        scraper = MigrosScraper()

        # Calling the scrape_and_parse method
        result = scraper.scrape_and_parse()

        # Assertions: Expecting two products in the result
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'Test Product 1')
        self.assertEqual(result[0]['price'], '10.00')
        self.assertEqual(result[1]['name'], 'Test Product 2')
        self.assertEqual(result[1]['price'], '20.00')

        # Close the scraper
        scraper.close()

class TestMigrosParser(unittest.TestCase):
    
    def test_parser(self):
        """Test that MigrosParser can correctly parse product names and prices."""
        raw_html = """
        <html>
            <article class="product-card">
                <span data-cy="product-name-123">Test Product 1</span>
                <span data-cy="current-price">10.00</span>
            </article>
            <article class="product-card">
                <span data-cy="product-name-456">Test Product 2</span>
                <span data-cy="current-price">20.00</span>
            </article>
        </html>
        """
        # Instantiate the parser with the mock HTML
        parser = MigrosParser(raw_html)
        result = parser.parse()

        # Assertions: Expecting two products in the result
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'Test Product 1')
        self.assertEqual(result[0]['price'], '10.00')
        self.assertEqual(result[1]['name'], 'Test Product 2')
        self.assertEqual(result[1]['price'], '20.00')

if __name__ == '__main__':
    unittest.main()
