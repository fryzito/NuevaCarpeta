from bs4 import BeautifulSoup
import requests
import time
from random import randint
import shutil 
import os, errno
import re

from selenium import webdriver

# These two will be implemented by us
from logger import Logger
from processor import Processor

class Proetica(object):
    
    def __init__(self, url):
    # This will be implemented by us, just like the logger
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
        self.directory = 'ProeticaOutPut'
        self.create_directory(self.directory)


    def create_directory(self, directory):
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise 

    def get_page(self, url):
        """
        This just requests the given URL and returns the respons econtent.

        Make sure to log if the request returns something other than 200.
        """

        try:
            #print(url);
            #url = 'http://www.inforegion.pe/252142/lluvias-aisladas-de-moderada-intensidad-en-el-norte-de-loreto/'
            response = self.request_session.get(url, headers = self.req_headers)
            print('get_page:url')
            #print(url)
            #print(response)
            #print('salir response');
            if response.ok == False:
                self.logger.request_failed(url, response)
                return None
         
            return response.content
        except Exception:
            # Log that the request failed and why
            #print('response')
           # print(response)
            self.logger.request_failed(url, response)
        

    def sleep_script(self,mini, maxi):
        script_sleep = randint(mini, maxi)
        self.logger.custom('Script is going to sleep for %d seconds.' % script_sleep)
        time.sleep(script_sleep)


    def get_index_content(self, page_content, page_url):
        

        self.logger.scraping_item(url)
        print('Scraping %s' % url)

        soup = BeautifulSoup(page_content,'lxml')

        
        result = {
            'title': '',
            'second_title':'',
            'author': '',
            'datetime': '',
            'description': '', 
            'html': str(soup), 
            'files': [],
            'location':'',
            'url':url
        }

        title = None
        second_title = None
        author = None
        datetime = None
        description = None
        files = []
        images = []
        location = None


        try:
            title = soup.h1.text
        except:
            self.logger.custom('Could not find field "title" in: %s' % url)

        try:
            second_title = soup.h2.text
        except:
            self.logger.custom('Could not find field "second title" in: %s' % url)

        try:
            author = '' #soup.select_one('').text
        except:
            self.logger.custom('Could not find field "author" in: %s' % url)

        #try:
            #loc_date_string = soup.select_one('div.content-single span.box-date').text
            #index_of_date = re.search("\d", loc_date_string)
            #location = loc_date_string[0:index_of_date.start()]
            #datetime = loc_date_string[index_of_date.start():].split(',')[0]
        #except:
            #self.logger.custom('Could not find field "datetime" in: %s' % url)
        

        try:
            body = soup.body
            description = body.p.get_text()

            
        except:
            self.logger.custom('Error processing description in: %s' % url)


        try:

            son_list = []

            for index,tags in enumerate(body.descendants):
                son_list.append(tags)
            

            first_son = son_list[791]

            f_div = first_son.div
        
            list_div = []
            for index,sibling in enumerate(first_son.div.next_siblings):
                if sibling != '\n':
                    list_div.append(sibling)
            

            imagen = list_div[9]
            #print(list_div[9])

            image_url = imagen.a.img['src']
            #print(URLs)

            image_name = re.sub(r'\W+', '', image_url)+'.jpg'
            image_path = os.path.join(self.directory, image_name) 

            #print(image_name)
            #print(image_path)

            #try: 
                #Most images don't have text so its pointless to save them and send to fscrawler 
            #    self.download_image(image_url,image_path)
            #    images.append(image_path)
            #    print('Downloaded image')
            #except: 
            #    self.logger.custom('Could not download the photo in: %s' % url)
        except:
            self.logger.custom('Could not find field "image_path" in: %s' % url)

        result['title']= title
        result['second_title']= second_title
        result['author']= author
        result['datetime']= datetime
        result['description']= description
        result['files']= files
        result['images']= images
        result['location']= location


        '''
        print("result['title']:",result['title'],'\n')
        print("result['second_title']:",result['second_title'],'\n')
        print("result['author']:",result['author'],'\n')
        print("result['datetime']:",result['datetime'],'\n')
        print("result['description']:",result['description'],'\n')
        #print("result['html']:",result['html'],'\n')
        print("result['files']:",result['files'],'\n')
        print("result['location']:",result['location'],'\n')
        print("result['url']:",result['url'],'\n')
        ''' 

        self.processor.save_on_json(result, self.directory)
        # Send result to processor
        self.processor.send(result, self)

        # Log that results were sent
        self.logger.result_sent(result)
        self.sleep_script(1,4)


    def find_items_in_page(self, page_url, driver):
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

        print("Inicializando driver para la url:", page_url)


        driver.get(page_url)
        self.sleep_script(2,5)

        try:
            if(page_url[len(page_url)-2] != '0'):
                button = driver.find_element_by_xpath("//div[@id='interface']/div[@id='content-container']/div[@id='contentwrap']/div[@class='colleft']/div[@id='objContents']/div[@class='modHTM']/p[3]/a[8]")
            else:
                button = driver.find_element_by_xpath("//div[@id='interface']/div[@id='content-container']/div[@id='contentwrap']/div[@class='colleft']/div[@id='objContents']/div[@class='modHTM']/p[2]/a[9]")
        except:
            print(' except on driver.find ')

        self.sleep_script(2,5)

        url_son = button.get_property("href")

        # para sacar los links con soup
        print(url_son)
        current_son_page = self.get_page(url_son)

        items = []

        # extraer los link de la pagina
        sub_soup = BeautifulSoup(current_son_page,'lxml')

        body = sub_soup.body
        links = body.find_all('a')

        # Se deja afuera los que no son URLs validar esto una vez hecha click con selenium
        size = len(links)-4
        for cont,link in enumerate(links):
            if cont >= 4 and cont < size :
                aux = url_son[:27]+link.get('href')
                items.append(aux)
            
        

        # pasar a la siguiente pesta;a con el botton siguiente (OJO falta) limpiar los que no son links

        # Log the items found
        self.logger.found_items_in_page(items, page_url)
        
        return items

    def scrape_items(self, items):
        """
        This gets the DOM elements for the items and extracts the link
        to the actual page. You can implement this however you like but
        remember to log any unexpected behavior
        """

        for url_item in items:
            if url_item:
                self.scrape_item(url_item)
            else:
                self.logger.custom('Could not find url_item in item: %s', url_item)
                pass
                # log error. href not found


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

        # Log that the individual scraping begins
        self.logger.scraping_item(url)
        print('Scraping %s' % url)

        response = requests.get(url)
        soup = BeautifulSoup(response.content,'lxml')

        
        # Content attributes
        list_attribs = ['periodo', 'legislatura', 'fecha presentacion', 'numero', 'proponente', 'grupo ', 'titulo',  'sumilla', 'autores', 'adherentes', 'seguimiento', 'iniciativas' ]

        description_content = {
            'periodo': '',
            'legislatura': '',
            'fecha presentacion': '',
            'numero': '',
            'proponente': '', 
            'grupo': '', 
            'titulo': '',
            'sumilla': '',
            'autores': '',
            'adherentes': '',
            'seguimiento': '',
            'iniciativas': ''
        }

        table = soup.find('table')
        
        cont = 0
        for index,tags in enumerate(table.descendants):
            if tags.name == "tr":
                tags = tags.table
                if tags:
                    for tr_index,tr_tags in enumerate(tags.descendants):
                        td = tr_tags.find('td')
                        if td and td != -1:
                            # Primer attributo del row de la tabla
                            #print('td 1 :',td.get_text())
                            # Segundo attributo del row de la tabla
                            #print('td 2 :',td.next_sibling.get_text())
                            description_content[list_attribs[cont]] = td.next_sibling.get_text()
                            cont = cont + 1
                            if cont == len(list_attribs):
                                break


        #print('description',description_content)


        result = {
            'title': '',
            'second_title':'',
            'author': '',
            'datetime': '',
            'description': '', 
            'html':response.text, 
            'files': [],
            'location':'',
            'url':url
        }

        # merge attributes
        title = description_content['titulo']
        second_title = description_content['periodo']+' '+ description_content['legislatura']+' '+ description_content['numero']+' '+ description_content['fecha presentacion']
        author = ' autores: '+description_content['autores']+' grupo: '+ description_content['grupo']+' adherentes: '+ description_content['adherentes']+' proponente: '+description_content['proponente']
        datetime = None
        description = description_content['seguimiento']+' '+ description_content['sumilla']
        files = []
        images = []
        location = None

        result['title']= title
        result['second_title']= second_title
        result['author']= author
        result['datetime']= datetime
        result['description']= description
        result['files']= files
        result['images']= images
        result['location']= location

        #print(result)
        # Send result to processor
        self.processor.save_on_json(result, self.directory)
        self.processor.send(result, self)
        # Log that results were sent
        self.logger.result_sent(result)
        print(result)
        print('sucessfully')
        print('')
        self.sleep_script(1,3)

        
    def run(self):
        """
        This is the main method. Your scraper should always run like this:
        scraper.run()

        Don't forget to call self.logger.start_scraping_run(self) at the
        beginning of this function also.

        In this example pagination is handled here
        """

        # Remember to pass the scraper object to the Logger when first
        # initializing it
        self.logger = Logger(self)

        self.logger.start_scraping_run(
            paginated=False
        ) # set paginated=True if this scraper has pagination

        current_page = self.get_page(self.url)

        #print(current_page)
        ## Log the URL of the next page
        self.logger.looking_for_items_in_page(self.url)
        
        # Link para provar la recoleccion de la tabla
        ##str_prove = 'http://www2.congreso.gob.pe/Sicr/TraDocEstProc/CLProLey2016.nsf/641842f7e5d631bd052578e20058a231/db5f4db0c7192b8805258005006c32ae?OpenDocument'
        ##self.scrape_item(str_prove)

        
        try:
            #print(current_page)
            while current_page:
                
                result = self.get_index_content(current_page, self.url)
                # iterar  entre pesta;as

                soup = BeautifulSoup(current_page,'lxml')
                body = soup.body
                periots = body.h3
                lists_a = periots.find_all('a')
                # links by periots # loop para cambiar de ventanas
                driver = webdriver.Chrome('/home/amigocloud/Documentos/ChromeDriver/chromedriver')
                
                items = self.find_items_in_page(self.url, driver)

                self.scrape_items(items) # <+====


                for links in lists_a:

                    url_string_srt = str(links['href'])

                    prefix = "http://www.congreso.gob.pe/"
                    # /Docs/spa/../../pley-2006-2011/
                    prefix = prefix + url_string_srt[16:]
                    
                    items = []
                    print(prefix)
                    items = self.find_items_in_page(prefix, driver)

                    result = self.scrape_items(items) # <+====

                

                driver.close()
                print('salio de drive.close()')
                print('salio')
                
                break # salir del while

                

        except:
            print('except')
            # If anything happens to interrupt the scraping: log it
            self.logger.unexpected_termination()


        # Log that the scraping finished successfully
        self.logger.finished_scraping_run()
        

if __name__ == '__main__':
    
    url = 'http://www.congreso.gob.pe/pley-2016-2021'
    scraper = Proetica(url)
    scraper.run()
    
