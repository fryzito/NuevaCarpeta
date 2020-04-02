from bs4 import BeautifulSoup
import requests
from random import randint
from selenium import webdriver
import json
import os, errno
import time

from selenium import webdriver
from selenium.webdriver.support.ui import Select

# These two will be implemented by us
from logger import Logger
from processor import Processor

class scraper_class(object):
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



	def get_text_list_in_drop_down(self, drop_down):
		ans = []
		for tag in drop_down.descendants:
			if tag.name == 'option':
				ans.append(tag.get_text())
		return ans


	def get_items(self, str_html):

		soup = BeautifulSoup(str_html,'lxml')

		head = soup.head
		body = soup.body

		items = []

		if head.get_text() == '':
			print('None on current page')
			return None
		else:
			# list all items
			print('Entro porque encontro texto en head')
			items_by_page = body.find_all('tbody')
			print('La longitud de items by pague es:')
			print(len(items_by_page))
			for item in items_by_page:
				print('-------items by pague ------')
				if item.find('tbody') != None:
					items.append(item)
					print(len(items))
				else:
					print('item.find(tbody)')
					print(item.find('tbody'))

			# pagination enough

		return items


	def get_items_in_drop_down(self, current_page):
		items = []
		soup = BeautifulSoup(current_page,'lxml')
		body = soup.body

		content_box = body.find('div', {'class':'content-page'})

		drop_down1 = content_box.find('select', {'id':'selAnhoNormativa'})
		drop_down2 = content_box.find('select', {'id':'selMesNormativa'})

		# obtain drop drow elements
		years = self.get_text_list_in_drop_down(drop_down1)
		months = self.get_text_list_in_drop_down(drop_down2)

		print(years)
		print(months)

		# use selenium for iterate beetween all items
		driver = webdriver.Chrome('/home/amigocloud/Documentos/ChromeDriver/chromedriver')
		driver.get(self.url)
		self.sleep_script(2,3)

		# change drop down
		for year in years:
			
			button = driver.find_element_by_xpath('//*[@id="selAnhoNormativa"]')
			Select(button).select_by_visible_text(year)
			for month in months:
				
				button2 = driver.find_element_by_xpath('//*[@id="selMesNormativa"]')
				Select(button2).select_by_visible_text(month)
				self.sleep_script(1,2)

				# extract item
				iframe = driver.find_element_by_tag_name("iframe")
				driver.switch_to.frame(iframe)

				html = driver.page_source

				# obtain item
				items_on_one_combination_of_drop_down = self.get_items(html)

				if items_on_one_combination_of_drop_down:
					print('add to items')
					# do for for append items
					items = items + items_on_one_combination_of_drop_down
					print(len(items))
				
				driver.switch_to.default_content()
		
		driver.close()

		return items


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
				
				# obtain items 
				items = self.get_items_in_drop_down(current_page)
				print('number of items:')
				print(items)

				# procesar los items


				break

		except Exception as e:
			print(e)
			print('exception no entro al while:')


if __name__ == '__main__':

	url1 = 'http://www.contraloria.gob.pe/wps/wcm/connect/cgrnew/as_contraloria/as_portal/publicaciones/as_boletin_contra'

	scraper = scraper_class(url1)
	scraper.run(1)

