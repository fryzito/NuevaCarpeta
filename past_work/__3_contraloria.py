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

		
	#def run_first(self):
	#	print("something first")

	#def run_second(self):
	#	print("something second")

	#def run_third(self):
	#	print("something third")

	def download_file(self, url,downloadPath):
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



	def run_quarter(self,id_page):
		self.logger = Logger(self)

		self.logger.start_scraping_run(
			paginated=False
		) # set paginated=True if this scraper has pagination

		current_page = self.get_page(self.url)

		try:	
			while current_page:
				
				
				# buscar item en la pagina item tiene urls
				items = []
				soup = BeautifulSoup(current_page)
				body = soup.body
				content_box = body.find('div', {'class':'content-page'})

				# extract labels a
				list_a = content_box.find_all('a')
				for th_a in list_a:
					if(th_a['href'].find('.pdf')!=-1):
						print(th_a['href'])
						items.append(th_a['href'])

				# iterar entre las componentes
				list_sub_div = content_box.findAll('div', {'class':'col-md-5'})
				cont = 0
				for sub_div in list_sub_div:
					if sub_div.center:

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



						# files extraer pdf

						files = []
						try:
							# url del pdf
							pdf_url =  sub_div.find('a')['href']

							pdf_name = pdf_url.split('/')[-1]

							# Name validation
							pdf_name = self.clean_url(pdf_name)

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


				current_page = None

		except Exception as e:
			print('exception no entro al while :')


	def run_fifth(self):
		print("something fifth")

	def run_first(self):
		print("something first")
		


if __name__ == '__main__':

	#url = 'http://www.contraloria.gob.pe/wps/wcm/connect/cgrnew/as_contraloria/as_portal/publicaciones'

	# url1 = http://www.contraloria.gob.pe/wps/wcm/connect/cgrnew/as_contraloria/as_portal/publicaciones/as_boletin_contra
	# url2 = http://www.contraloria.gob.pe/wps/wcm/connect/cgrnew/as_contraloria/as_portal/publicaciones/as_libros
	# url3 = http://www.contraloria.gob.pe/wps/wcm/connect/cgrnew/as_contraloria/as_portal/publicaciones/as_memorias
	url4 = 'http://www.contraloria.gob.pe/wps/wcm/connect/cgrnew/as_contraloria/as_portal/publicaciones/as_inf_gestion'
	# url5 = 'http://www.contraloria.gob.pe/wps/wcm/connect/cgrnew/as_contraloria/as_portal/publicaciones/as_trab_investigacion'


	scraper = contraloria(url4)
	scraper.run_quarter(4)

