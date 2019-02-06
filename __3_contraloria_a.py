from bs4 import BeautifulSoup
import requests
from random import randint
from selenium import webdriver
import json
import os, errno
import time

# These two will be implemented by us
from logger import Logger
from processor import Processor

class contraloria(object):
	def __init__(self, url):
		self.dir_url = url
		self.processor = Processor()
		self.logger = None
		self.url = url
		self.request_session = requests.session()
		self.req_headers = {
			'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
			'accept-encoding': 'gzip, deflate',
			'accept-language': 'en-US,en;q=0.9,ar;q=0.8',
			'Cache-Control': 'max-age=0',
			'Host':'urbantoronto.ca',
			'upgrade-insecure-requests': '1',
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
		}
		self.directory = 'contraloriaOutPut'
		self.create_directory(self.directory)
		self.cont = 0

	def create_directory(self, directory):
		try:
			if not os.path.exists(directory):
				os.makedirs(directory)
		except OSError as e:
			if e.errno != errno.EEXIST:
				raise

	def sleep_script(self,mini, maxi):
		script_sleep = randint(mini, maxi)
		self.logger.custom('Script is going to sleep for %d seconds.' % script_sleep)
		time.sleep(script_sleep)


	def get_page(self, url):

		try:
			response = self.request_session.get(url, headers = self.req_headers)
			if response.ok == False:
				self.logger.request_failed(url, response)
				return None

			return response.content

		except Exception as e:
			# Log that the request failed and why
			self.logger.request_failed(url, response)


	def scrape_item(self, url, index_item, id_items):
		print('something')


	def download_file(self, url,downloadPath):
		#print(url,' ',downloadPath)
		r = requests.get(url, stream=True)
		with open(downloadPath, 'wb') as f:
			for chunk in r.iter_content(chunk_size=1024):
				if chunk:
					f.write(chunk)

	def clean_url(self, pdf_name):
		# Name validation
		pdf_name = pdf_name.replace('?','')
		pdf_name = pdf_name.replace('|','')
		pdf_name = pdf_name.replace('>','')
		pdf_name = pdf_name.replace('<','')
		pdf_name = pdf_name.replace('/','')
		pdf_name = pdf_name.replace(':','')
		pdf_name = pdf_name.replace('"','')
		pdf_name = pdf_name.replace('*','')

		return pdf_name


	def run(self,id_page):
		"""
        This is the main method. Your scraper should always run like this:
        scraper.run()

        Don't forget to call self.logger.start_scraping_run(self) at the
        beginning of this function also.

        In this example pagination is handled here
        """

		self.logger = Logger(self)
		self.logger.start_scraping_run(
			paginated=False
		) # set paginated=True if this scraper has pagination

		current_page = self.get_page(self.url)

		try:
			while current_page:
				# buscar item en la pagina item tiene urls
				items = []
				soup = BeautifulSoup(current_page,'lxml')
				body = soup.body

				content_box = body.find('div', {'class':'content-page'})

				print(content_box.h4)
				print(content_box.h2)



				break

		except Exception as e:
			print(e)
			print('exception no entro al while:')


if __name__ == '__main__':

	url1 = 'http://www.contraloria.gob.pe/wps/wcm/connect/cgrnew/as_contraloria/as_portal/publicaciones/as_memorias'

	scraper = contraloria(url1)
	scraper.run(1)

