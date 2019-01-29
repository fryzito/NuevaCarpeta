from abc import ABCMeta, abstractmethod
import requests


class Scraper(metaclass=ABCMeta):
    @abstractmethod
    def scrape_item(self, url):
        """
        This method actually retrieves the data form the item itself and sends
        the json to the Processor

        Remember to log:

        - That you started scraping this single item
        - If any fields were not found
        - If the request failed
        - That the json was sent to the processor
        - Any unexpected behavior
        """
        pass

    @abstractmethod
    def scrape_items(self, items):
        """
        This gets the DOM elements for the items and extracts the link
        to the actual page. You can implement this however you like but
        remember to log any unexpected behavior
        """
        pass
    
    @abstractmethod
    def find_items_in_page(self, page_content):
        """
        This method finds all scrapeable items in the current page. In this case
        this helps us get the URL to the item itself. In some cases there could
        even be additional info here not found on the article itself.

        *** IMPORTANT ***
        Always use try/catch if errors can happen. And if errors do happen make
        sure to send them to the logger.
        Also use if/else in cases where you expect BeautifulSoup to find
        something to log the case where it doesn't find anything.
        """
        pass

    def get_page(self, url):
        """
        This just requests the given URL and returns the response content.

        Make sure to log if the request returns something other than 200.
        """
        print(url)
        print('Hola Mundo desde getpage Scaper.py')
        response = requests.get(url)

        if response.status_code == 200:
            return response.content
        else:
            # Log that the request failed and why
            self.logger.request_failed(url, response)
            print(response.content)
            return None

    def next_page_url(self, page_content):
        pass

    @abstractmethod
    def run(self):
        """
        This is the main method. Your scraper should always run like this:
        scraper.run()

        Don't forget to call self.logger.start_scraping_run(self) at the
        beginning of this function also.

        In this example pagination is handled here
        """
        pass

    def search_title(self, result, soup):
        """
        This method is used to search and save the news title.
        """
        pass

    def search_subtitle(self, result, soup):
        """
        This method is used to search and save the news subtitle.
        """
        pass
    
    def search_authors(self, result, soup):
        """
        This method is used to search and save the news authors.
        """
        pass

    def search_time(self, result, soup):
        """
        This method is used to search and save the news time.
        """
        pass

    def search_body(self, result, soup):
        """
        This method is used to search and save the news body.
        """
        pass

    def search_tags(self, result, soup):
        """
        This method is used to search and save the news tags.
        """
        pass

    def search_images(self, result, soup):
        """
        This method is used to search and save the news images.
        """
        pass
