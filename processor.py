import base64
import hashlib
import os
import sys

import psycopg2

#from elasticsearch import Elasticsearch

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
#from celeryapp.tasks import ingestScrapedWebPageToElasticsearch,\
#    process_law_document, process_extracted_text

# This are the same as in django/backend/api/celery_pipeline/celeryapp/tasks.py
# and should be moved to a settings file or something.
ELASTICSEARCH_WEBPAGES_INDEX = 'webpages'
ELASTICSEARCH_HOST = 'elasticsearch'
ELASTICSEARCH_PORT = 9200

METABASE_DBINFO = {
    "host": "postgresmetabase",
    "port": 5432,
    "user": "metabase",
    "password": "ArMBRGgvVhUhQMaYdjRa2MM3zx8KcSyvhg34",
    "database": "metabase",
}


class Processor:
    def __init__(self):
        pass

    def exists_in_elasticsearch(self, id_, index=ELASTICSEARCH_WEBPAGES_INDEX, doc_type="doc"):
        print("pass exists_in_elasticsearch")

    def check(self, url, scraper):
        print("pass check")


    def is_file_indexed(self, filename, scraper):
        print("pass is_file_indexed")

    def send(self, result, scraper):
        #print(result)
        #print(result['title'])
        #print(result['html'])
        print("pass result")

    def process_el_peruano_document(self, document, scraper):
        # Unused fields
        print("pass process_el_peruano_document")

    @staticmethod
    def _get_ddl(table_name, headers, row):
        print("pass _get_ddl")

    @staticmethod
    def send_metabase_table(name, headers, data):
        """Createss a table on metabase db and inserts data"""
        print("pass send_metabase_table")
