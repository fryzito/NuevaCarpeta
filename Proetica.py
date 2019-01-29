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
        #self.directory = 'inforegion/amazonia-2'
        #self.create_directory(self.directory)


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
        soup = BeautifulSoup(response.content)

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

        title = None
        second_title = None
        author = None
        datetime = None
        description = None
        files = []
        images = []
        location = None


        try:
            title = soup.select_one('div.content-single h1').text
        except:
            self.logger.custom('Could not find field "title" in: %s' % url)

        try:
            second_title = soup.select_one('div.content-single small').text
        except:
            self.logger.custom('Could not find field "second title" in: %s' % url)

        try:
            author = '' #soup.select_one('').text
        except:
            self.logger.custom('Could not find field "author" in: %s' % url)

        try:
            loc_date_string = soup.select_one('div.content-single span.box-date').text
            index_of_date = re.search("\d", loc_date_string)
            location = loc_date_string[0:index_of_date.start()]
            datetime = loc_date_string[index_of_date.start():].split(',')[0]
        except:
            self.logger.custom('Could not find field "datetime" in: %s' % url)

        try:
            body = ''
            body_lis = soup.select ('div.content-single ul li')
            if body_lis != None and len(body_lis) > 0:
                temp = [li.text  for li in body_lis if li.text != "" ]
                body += '\n'.join(temp)

            body_ps = soup.select('div.content-single p')
            if body_ps != None and len (body_ps) > 0 :
                temp = [p.text for p in body_ps if p.text != "" ]
                body += '\n'.join(temp)

            body_h4 = soup.select('div.content-single.h4')
            if body_h4 != None and len(body_h4) > 0:
                temp = [h4.text for h4 in body_h4 if h4.text != ""]
                body += '\n'.join(temp)
            
            description = body

            
        except:
            self.logger.custom('Error processing body in: %s' % url)


        try:
            image_url  = soup.select_one('div.content-single div.description-img div.img_wrapper.center img')['src']
            image_name = re.sub(r'\W+', '', image_url)+'.jpg'
            image_path = os.path.join(self.directory, image_name) 
            try: 
                #Most images don't have text so its pointless to save them and sned to fscrawler 
                self.download_image(image_url,image_path)
                images.append(image_path)
            except: 
                self.logger.custom('Could not download the photo in: %s' % url)
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

        # Send result to processor
        self.processor.send(result, self)
        # Log that results were sent
        self.logger.result_sent(result)
        self.sleep_script(1,4)


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
            self.logger.custom('Error processing body in: %s' % url)


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

        # Send result to processor
        self.processor.send(result, self)
        # Log that results were sent
        self.logger.result_sent(result)
        self.sleep_script(1,4)


    def find_items_in_page(self, page_content, page_url):
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
        soup = BeautifulSoup(page_content,'lxml')

        body = soup.body
        
        periots = body.h3

        lists_a = periots.find_all('a')

        # links by periots
        list_links = []
        for links in lists_a:
            list_links.append(links['href'])
        
        # paginado
        # creando driver
        driver = webdriver.Chrome('/home/amigocloud/Documentos/ChromeDriver/chromedriver')
        driver.get(page_url)
        sleep(2)
        button = driver.find_element_by_link_text('')
        button.click()
        sleep(5)
        driver.close()


        #for article in body:
        #    link = article.select_one('a')
        #    print(link)

            #items.append({
            #        'article': article,
            #        'url': link   
            #})
            #print('items')
            #print(items)
            #print('FIN items')


        # Log the items found
        self.logger.found_items_in_page(items, page_url)

        return items


        
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
        
        try:
            #print(current_page)
            while current_page:
                
                result = self.get_index_content(current_page, self.url)
                
                items = self.find_items_in_page(current_page, self.url )

                print(items)
                #result = self.scrape_items(items) # <+====
                #print('despues de results')
                #print(result)
                #next_page_url = self.next_page_url(current_page)

                if not next_page_url:
                    break

                # Log the URL of the next page
                self.logger.looking_for_items_in_page(next_page_url)
                #current_page = self.get_page(next_page_url)
                
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
    
