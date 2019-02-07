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


	def scrape_item(self, current_container):

		rows = current_container.find_all('tr')

		for row in rows:

			result = {
				'title': '',
				'second_title':'',
				'author': '',
				'datetime': '',
				'description': '',
				'html':str(current_page),
				'files': [],
				'location':'',
				'url':self.url
			}
			try:
				title = sub_div.p.get_text() 
			except e:
				self.logger.custom('Could not find field "title" in: %s' % self.url)

			try:
				description = content_box.h2.get_text() +' '+ content_box.h4.get_text() +' '+ sub_div.p.get_text()
			except:
				self.logger.custom('Could not find field "description" in: %s' % self.url)

	 		# second tittle

			# files extraer pdf
			files = []
			try:
				# url del pdf
				pdf_url =  sub_div.find('a')['href']

				pdf_name = pdf_url.split('/')[-1]

				# Name validation
				pdf_name = self.clean_url(pdf_name)


				'''
				## directory + dirName+ fileName
				 pdf_path = os.getcwd() +'/'+self.directory + '/' + pdf_name
							try:
								self.download_file(pdf_url,pdf_path)
								files.append(pdf_path)
							except: 
								self.logger.custom('Could not download the PDF  in: %s' % url)

						except:
							self.logger.custom('Could not find field "PDF" in: %s' % url)


						result['title'] = title
						result['second_title']= content_box.h2.get_text() +' '+ content_box.h4.get_text()
						result['author']= ''						
						result['datetime']= ''			
						result['description']= description
						result['files']= files						
						result['images']= ''						
						result['location']= ''
						#print(result)

						# Send result to processor
						self.processor.save_on_json(result, self.directory, cont, id_page)
						cont = cont + 1

						# send data
						self.processor.send(result, self)

						# Log that results were sent
						self.logger.result_sent(result)
						print('sucessfully')
						print('')
				'''


	def download_file(self, url,downloadPath):
		#print(url,' ',downloadPath)
		r = requests.get(url, stream=True)
		with open(downloadPath, 'wb') as f:
			for chunk in r.iter_content(chunk_size=1024):
				if chunk:
					f.write(chunk)

	def clean_url(self, file_name):
		# Name validation
		file_name = file_name.replace('?','')
		file_name = file_name.replace('|','')
		file_name = file_name.replace('>','')
		file_name = file_name.replace('<','')
		file_name = file_name.replace('/','')
		file_name = file_name.replace(':','')
		file_name = file_name.replace('"','')
		file_name = file_name.replace('*','')

		return file_name


	def get_text_list_in_drop_down(self, drop_down):
		ans = []
		for tag in drop_down.descendants:
			if tag.name == 'option':
				ans.append(tag.get_text())
		return ans


	def get_items_on_iframe(self, str_html):

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

			# filtrar por tbody puede estar mal
			for item in items_by_page:
				#print('--------comienza iteracion--------------------')
				#print(item)
				#print('-------items by pague ------')
				#print(type(item))
				#print(item.find_all('tr'))
				if item.find('tr') != None:
					items.append(item)
					#print('longitud de items')
					#print(len(items))
				#else:
				#	print('item.find(tbody) es None')
				#	print(item.find('tr'))

			# pagination enough

		return items


	def get_items_in_drop_down(self, current_page):
		items_on_view = []
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
		driver = webdriver.Chrome('chromedriver')
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
				items_on_one_combination_of_drop_down = self.get_items_on_iframe(html)

				if items_on_one_combination_of_drop_down:
					print('add to items')
					# do for for append items
					items_on_view = items_on_view + items_on_one_combination_of_drop_down
					print('items acumulados: ',len(items_on_view))
				
				driver.switch_to.default_content()

			break
		
		driver.close()

		return items_on_view

	def scrape_items(self, items):
		"""
        This gets the DOM elements for the items and extracts the link
        to the actual page. You can implement this however you like but
        remember to log any unexpected behavior
        """
		for container in items:
			if container:
				self.scrape_item(container)
			else:
				self.logger.custom('Could not find container in item: %s', container)
				pass

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
				items_on_pague = self.get_items_in_drop_down(current_page)
				print('number of items to process:',len(items_on_pague))

				# procesar los items
				self.scrape_items(items_on_pague)




				break

		except Exception as e:
			print(e)
			print('exception no entro al while:')


if __name__ == '__main__':

	url1 = 'http://www.contraloria.gob.pe/wps/wcm/connect/cgrnew/as_contraloria/as_portal/publicaciones/as_boletin_contra'

	scraper = contraloria(url1)
	scraper.run(1)

