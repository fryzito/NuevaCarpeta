import logging
import sys
import traceback
from datetime import datetime

import requests

logger = logging.Logger(__name__)

# We need to change authorization for the logger. IP based?
LOG_RECORD_API_SETTINGS = {
    'host': 'django',
    'port': 80,
    'endpoint': 'genesisapi/scrapers/log_record/',
    'protocol': 'http',
    'authtoken': 'cb8cc66b41c024b68b8a744721c2a8b0e2205fd0',
}


class RequestsHandler(logging.Handler):
    def __init__(self, host, port, endpoint, protocol, authtoken):
        print("passed init")

    def emit(self, record):
        print("passed emit")

    def build_log_record(self, record):
        print("passed build_log_record")


class Logger:
    def __init__(self, scraper):
       print("passed init")

    def start_scraping_run(self, paginated=False):
        print("passed start_scraping_run")
        
    def scraping_item(self, url):
        print("passed scraping_item")

    def result_sent(self, result):
        print("passed result_sent")

    def found_items_in_page(self, items, page_url):
        print("passed found_items_in_page")

    def request_failed(self, url, response):
        print("passed request_failed")

    def looking_for_items_in_page(self, url):
        print("passed looking_for_items_in_page")

    def unexpected_termination(self):
        print("passed unexpected_termination")

    def finished_scraping_run(self):
        print("passed finished_scraping_run")

    def custom(self, custom_message):
        print("passed custom")

