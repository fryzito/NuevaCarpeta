from bs4 import BeautifulSoup
import requests
import time
from random import randint
import shutil 
import os, errno
import re
import urllib.request

# These two will be implemented by us
from logger import Logger
from processor import Processor

class PoderJudicial(object):
    
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

        self.baseUrl = 'http://www.pj.gob.pe'
        self.directory = 'PoderJudicialOutPut'
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

            response = self.request_session.get(url, headers = self.req_headers)
            
            if response.ok == False:
                self.logger.request_failed(url, response)
                return None
         
            return response.content
        except e:
            print(e)
            # Log that the request failed and why
            self.logger.request_failed(url, response)
        

    def sleep_script(self,mini, maxi):
        script_sleep = randint(mini, maxi)
        self.logger.custom('Script is going to sleep for %d seconds.' % script_sleep)
        time.sleep(script_sleep)


    def find_items_in_page(self, current_page, page_url):
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

        ## iterar  entre la paginacion
        soup = BeautifulSoup(current_page,'lxml')
        body = soup.body

        # soup.find("div", {"id": "articlebody"})
        div_items = body.find_all('div')

        items = []
        #list_items = body.find_all("div")
        for div_element in div_items:
            if div_element.get('id')!= None:
                if div_element['id'] == 'content':
                    # Extraer
                    for index,tags in enumerate(div_element.descendants):
                        if(tags.name!=None and tags.name=='div'):
                            if(tags.get('id')!= None and tags.get('id')=='listRes'):
                                items.append(tags)
        
        return items

    def scrape_items(self, items):
        """
        This gets the DOM elements for the items and extracts the link
        to the actual page. You can implement this however you like but
        remember to log any unexpected behavior
        """

        for item in items:
            if item:
                self.scrape_item(item)
            else:
                self.logger.custom('Could not find url_item in item: %s', url_item)
                pass


    def download_file(self, url,downloadPath):

        r = requests.get(url, stream=True)
        
        #print('downloadPath ',downloadPath)

        with open(downloadPath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024): 
                if chunk: 
                    f.write(chunk)    



    def scrape_item(self, item):
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
        # Content attributes

        result = {
            'title': '',
            'second_title':'',
            'author': '',
            'datetime': '',
            'description': '',
            'html': item.text,
            'files': [],
            'location':'',
            'url': self.baseUrl + item.find('a')['href']
        }

        try:
            title = item.h4.text
        except:
            self.logger.custom('Could not find field "title" in: %s' % url)

        try:
            description = item.p.text

        except:
            self.logger.custom('Error processing description in: %s' % url)

        files = []

        try:
            pdf_url =  self.baseUrl + item.find('a')['href']
            pdf_name = pdf_url.split('/')[-1]

            # Name validation
            pdf_name = pdf_name.replace('?','')
            pdf_name = pdf_name.replace('|','')
            pdf_name = pdf_name.replace('>','')
            pdf_name = pdf_name.replace('<','')
            pdf_name = pdf_name.replace('/','')
            pdf_name = pdf_name.replace(':','')
            pdf_name = pdf_name.replace('"','')
            pdf_name = pdf_name.replace('*','')

            ## directory + dirName+ fileName 
            pdf_path = os.getcwd() +'/'+self.directory + '/' + pdf_name

            try: 
                self.download_file(pdf_url,pdf_path)
                files.append(pdf_path)

            except: 
                self.logger.custom('Could not download the PDF  in: %s' % url)
        except:
            self.logger.custom('Could not find field "PDF" in: %s' % url)


        ## Data without content
        second_title = None
        author = None
        datetime = None
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

        #print('resutado:')
        #print(result)

        # Send result to processor
        self.processor.save_on_json(result, self.directory)
        self.processor.send(result, self)
        # Log that results were sent
        self.logger.result_sent(result)
        print('successfully')
        print('')

    
    def next_page_url(self, current_page):
        
        soup = BeautifulSoup(current_page,'lxml')
        body = soup.body

        div_items = body.find_all('div')
        ans = ''
        #list_items = body.find_all("div")
        for div_element in div_items:
            if div_element.get('id')!= None:
                if div_element['id'] == 'content':
                    # Extraer
                    for index,tags in enumerate(div_element.descendants):
                        if(tags.name!=None and tags.name=='div'):
                            if(tags.get('id')!= None and tags.get('id')=='PiePagina'):
                                list_a = tags.find_all('a')

                                if len(list_a)==2:

                                    if(list_a[0]['id'].find('nextPage') != -1):
                                        ans = list_a[0].get('href')
                                    else:
                                        self.logger.custom("Could not find next page url")
                                        ans = None

                                else:
                                    ans = list_a[2].get('href')
        return ans

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
        
        try:

            while current_page:
                
                items = self.find_items_in_page(current_page, self.url)

                print(len(items))

                self.scrape_items(items)

                next_page_url = self.next_page_url(current_page)

                if not next_page_url:
                    break

                next_page_url = self.baseUrl+next_page_url

                # Log the URL of the next page
                self.logger.looking_for_items_in_page(next_page_url)
                current_page = self.get_page(next_page_url)
        except:
            # If anything happens to interrupt the scraping: log it
            self.logger.unexpected_termination()


        # Log that the scraping finished successfully
        self.logger.finished_scraping_run()


if __name__ == '__main__':


    #url = 'http://www.pj.gob.pe/wps/wcm/connect/SEDCF/s_sedcf/as_normatividad/'

    url1 = 'http://www.pj.gob.pe/wps/wcm/connect/sedcf/s_sedcf/as_normatividad/as_marco'
    url2 = 'http://www.pj.gob.pe/wps/wcm/connect/sedcf/s_sedcf/as_normatividad/as_especializado'
    url3 = 'http://www.pj.gob.pe/wps/wcm/connect/sedcf/s_sedcf/as_normatividad/as_materia'
    url4 = 'http://www.pj.gob.pe/wps/wcm/connect/sedcf/s_sedcf/as_normatividad/as_politicas'

    list_urls = [url1,url2,url3,url4]
    for links in list_urls:
        scraper = PoderJudicial(links)
        scraper.run()

    #scraper = PoderJudicial(url2)
    #scraper.run()
    
