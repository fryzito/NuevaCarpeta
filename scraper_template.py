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

class scraper(object):
	def __init__(self, url):
		self.dir_url = url
		self.processor = Processor()
		self.logger = None
		self.url = url
		self.baseUrl = 'https://procuraduriaanticorrupcion.minjus.gob.pe/'

		self.request_session = requests.session()
		self.req_headers = {
			'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
			'accept-encoding': 'gzip, deflate',
			'accept-language': 'en-US,en;q=0.9,ar;q=0.8',
			'Cache-Control': 'max-age=0',
			#'Host':'proetica.org.pe', # averiguar este attributo
			'upgrade-insecure-requests': '1',
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
		}

		self.directory = 'contraloriaOutPut'
		self.create_directory(self.directory)
		self.cont_global = 0

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


	def download_file(self, url,downloadPath):
		#print(url,' ',downloadPath)
		r = requests.get(url, stream=True)
		with open(downloadPath, 'wb') as f:
			for chunk in r.iter_content(chunk_size=1024):
				if chunk:
					f.write(chunk)



	def scrape_item(self, current_container, id_page):

		tbody = current_container.find('tbody')
		#print('paso1')
		print('paso2')
		rows = tbody.find_all('tr')
		

		for row in rows:
			
			# iterate throught table rows
			list_content = []

			# gather data
			print('paso3')
			cols_of_row = row.find_all('td')
			
			cont = 0
			for col in cols_of_row:

				# Recolectar infor de las columnas
				if cont == 5:
					print('col href != None')
					list_content.append(col.find('a')['href'])
				else:
					list_content.append(col.get_text())
					print('col href == None')
				cont = cont + 1

			#print('paso 3.5')

			print(list_content)

			result = {
				'title': '',
				'second_title':'',
				'author': '',
				'datetime': '',
				'description': '',
				'html':str(current_container),
				'files': [],
				'location':'',
				'url':self.url
			}

			#print('paso 3.5.1')

			try:
				title = list_content[2]
			except Exception as e:
				print(e)
				self.logger.custom('Could not find field "title" in: %s' % self.url)
				#print('paso 3.5.2')
			try:
				description = 'Numero: '+list_content[0]+' Tipo: '+ list_content[1]+ ' Sumilla: ' + list_content[2]+ ' Numero de informe: '+ list_content[3]+ ' Fecha: '+ list_content[5]
			except Exception as e:
				print(e)
				self.logger.custom('Could not find field "description" in: %s' % self.url)
			#print('paso 3.5.3')
			# second tittle
			try:
				second_title = list_content[1]
			except Exception as e :
				print(e)
				self.logger.custom('Could not find field "second title" in: %s' % self.url)

			#print('paso 3.6')

			# files extraer pdf
			files = []

			try:
				# url del pdf
				pdf_url =  list_content[5]

				pdf_name = pdf_url.split('/')[-1]

				# Name validation
				pdf_name = self.clean_url(pdf_name)

				## directory + dirName+ fileName
				pdf_path = os.getcwd() +'/'+self.directory + '/' + pdf_name

				#print(pdf_path)
				#print(pdf_url)

				try:
					self.download_file(pdf_url,pdf_path)
					files.append(pdf_path)
				except Exception as e:
					print(e)
					self.logger.custom('Could not download the PDF  in: %s' % pdf_url)

			except Exception as e:
				print(e)
				self.logger.custom('Could not find field "PDF" in: %s' % self.url)

			result['title'] = title
			result['second_title']= second_title
			result['author']= ''
			result['datetime']= ''
			result['description']= description
			result['files']= files
			result['images']= ''
			result['location']= ''

			#print('paso 3.7')

			#print(result)

			# Send result to processor
			self.processor.save_on_json(result, self.directory, self.cont_global, id_page)
			self.cont_global = self.cont_global + 1

			# send data
			self.processor.send(result, self)

			#print('paso 3.8')

			# Log that results were sent
			self.logger.result_sent(result)
			print('sucessfully')
			print('')

		print('paso el doble bucle completo ')
	

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

			#print('Entro porque encontro texto en head')
			if body.find('table') != None :
				items.append(body.find('table'))

				# Encontrar la segunda tabla 
				footer = body.find('div', {'class':'pagination center'})

				print('paso 4')
				
				list_a = footer.find_all('a')
				
				# pagination recursive
				for link_a in list_a:
					if link_a['id'].find('nextPage') != -1 :
						# ir a la pagina siguiente
						#print('Url siguiente pagina ',self.baseUrl, link_a['href'])
						current_page = self.get_page(self.baseUrl + link_a['href'])
						items = items + self.get_items_on_iframe(current_page)

		return items


	def get_items(self, current_page):
		items_on_view = []
		soup = BeautifulSoup(current_page,'lxml')
		body = soup.body

		content_box = body.find('div', {'class':'entry-content'})

		print(content_box)





		return items_on_view


	def scrape_items(self, items, id_page):
		"""
        This gets the DOM elements for the items and extracts the link
        to the actual page. You can implement this however you like but
        remember to log any unexpected behavior
        """
		for index, container in enumerate(items):
			if container:
				self.scrape_item(container,id_page)
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
				
				# Obtain items
				page_items = self.get_items(current_page)

				#print('number of items to process:',len(items_on_pague))

				# procesar los items
				#self.scrape_items(items_on_pague,id_page)

				break

		except Exception as e:
			print(e)
			print('exception no entro al while:')


if __name__ == '__main__':

	url = 'https://www.proetica.org.pe/contenido/encuesta-nacional-sobre-percepciones-de-la-corrupcion-en-el-peru/'
	scraper = scraper(url)

	# Id in which json files is writing
	scraper.run(1)
