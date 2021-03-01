""" A class that can be used to represent an amazon product page """

import bs4
import re
import requests
import time

from datetime import datetime

from select_user_agent import select_user_agent

from tools import get_price_from_bs4_object
from tools import get_id_from_url


class AmazonProductPage():
    """ A class representing an amazon product page """


    def __init__(self, id):
        
        self.id = id
        
        self.url = f'https://www.amazon.de/dp/{id}'
        
        self.amazon_base_url = f'https://www.amazon.de/dp/'
                
        self.country_code = None
        self.product_id = None
        self.product_category = None
        self.product_price = None
        self.product_seller_infos = None
        self.versand_durch_amazon = None
        self.kindle_edition = None
        self.kindle_price = None
        self.author = None
        self.title = None
        self.rauer_buchschnitt = None
        
        self.date = datetime.now().strftime('%Y-%m-%d')

        # object from BeautifulSoup (soup)
        self.bs4_object_product_page = None

        # initialize product page
        self.bs4_object_product_page = self.build_bs4_object(self.url)
                
        self.get_product_price()
        self.get_product_seller_infos()
        self.check_shipping_infos()
        self.get_kindle_edition()
        self.get_kindle_price()
        self.get_author()
        self.get_title()
        self.check_edition()
        
    
    def request_product_page(self, url):
        """ Request product page """
        
        user_agent = select_user_agent()
        headers = {'User-Agent': user_agent}
        
        r = requests.get(url, headers = headers)

        return r

    
    def build_bs4_object(self, url):
        """ Build object for BeautifulSoup """

        request_response = self.request_product_page(url)
        soup = bs4.BeautifulSoup(request_response.text, 'lxml')

        return soup


    def log_product_page(self, page):
        """ Log product page """

        # create log from amazon html code as a text file 
        with open(f'log/amz_{id}_{self.date}.txt', 'w', encoding='utf-8') as f:
            f.write(page.prettify())

    
    def get_product_price(self):
        """ Get price from product page """

        #try:
        #    price_text = self.bs4_object_product_page.find('span', class_='a-size-medium a-color-price offer-price a-text-normal').get_text(strip=True)
        #    price = search_price_in_text(price_text)
        #    price = format_price(price)
        #except:
        #    print('not text found for price')
        #    price = None

        #self.product_price = price

        r = self.bs4_object_product_page.find('span', class_='a-size-medium a-color-price offer-price a-text-normal')
        
        if not r:
            print('not text found for price')
            return None

        self.product_price = get_price_from_bs4_object(r)
        

    def get_product_seller_infos(self):
        """ Get merchant info from product page """
    
        r = self.bs4_object_product_page.find('div', id='merchant-info')
        
        try:
            self.product_seller_infos = r.get_text(strip=True)

        except:
            print('no text found for merchant info')
            self.product_price = None
                
    
    def check_shipping_infos(self):
        """ check if the item is shipped by amazon """

        if not self.product_seller_infos:
            print(f'check seller for id {self.url}')
            return None

        text = 'Versand durch Amazon'

        if text not in self.product_seller_infos:
            self.versand_durch_amazon = False
            self.product_price = None

    
    def get_author(self):
        """ Get author infos """

        r = self.bs4_object_product_page.find('a', class_='a-link-normal contributorNameID')
        
        if not r:
            print('not text found for author')
            return None

        author = r.get_text(strip=True)
        self.author = author

    
    def get_title(self):
        """ Get title """

        r = self.bs4_object_product_page.find('span', id='productTitle')
        
        if not r:
            print('not text found for title')
            return None
        
        title = r.get_text(strip=True).capitalize()
        self.title = title

    
    def check_edition(self):
        """ check edition """

        r = self.bs4_object_product_page.find('span', id='productSubtitle')
        
        if not r:
            print('not text found for more title information')
            return None
        
        subtitle  = r.get_text(strip=True)
        
        match = re.compile('Rauer Buchschnitt').search(subtitle)
        
        if match:
            print(f'{self.title}: schöne Edition')
            self.rauer_buchschnitt = True

        
    def get_kindle_edition(self):
        """ Get Kindle edition  """
        
        try:
            other_editions = self.bs4_object_product_page.find('span', class_="tmmShowPrompt", id="showMoreFormatsPrompt")
            """ HTML:
            
            <a class="title-text" href="/Thinking-Fast-English-Daniel-Kahneman-ebook/dp/B00555X8OA/">
                <span class="a-size-small a-color-base">Kindle</span>
                <span class="tmmAjaxLoading" id="tmmSpinnerDiv_1" style="display: none"></span></a>, 
            
            <a class="title-text" href="/Thinking-Fast-and-Slow/dp/B00NTQ3QX0/">
                <span class="a-size-small a-color-base">Audible Hörbuch, Ungekürzte Ausgabe</span>
                <span class="tmmAjaxLoading" id="tmmSpinnerDiv_2" style="display: none"></span></a>, 
            
            <a class="title-text" href="/Daniel-Kahneman/dp/0141033576/">
                <span class="a-size-small a-color-base">Taschenbuch</span>
                <span class="tmmAjaxLoading" id="tmmSpinnerDiv_4" style="display: none"></span></a>
            
            """
            
            kindle = other_editions.find_next('span', class_='a-size-small a-color-base', string='Kindle')
            kindle_link = kindle.parent['href']
            
            kindle_edition = get_id_from_url(kindle_link)

            self.kindle_edition = kindle_edition

        except:
            print('kindle edition not found')


    def get_kindle_price(self):
        """ Get Kindle price  """
        
        try:
            other_editions = self.bs4_object_product_page.find('span', class_="tmmShowPrompt", id="showMoreFormatsPrompt")
            """ HTML:
            
            <a class="title-text" href="/Thinking-Fast-English-Daniel-Kahneman-ebook/dp/B00555X8OA/">
                <span class="a-size-small a-color-base">Kindle</span>
                <span class="tmmAjaxLoading" id="tmmSpinnerDiv_1" style="display: none"></span></a>, 
            
            <a class="title-text" href="/Thinking-Fast-and-Slow/dp/B00NTQ3QX0/">
                <span class="a-size-small a-color-base">Audible Hörbuch, Ungekürzte Ausgabe</span>
                <span class="tmmAjaxLoading" id="tmmSpinnerDiv_2" style="display: none"></span></a>, 
            
            <a class="title-text" href="/Daniel-Kahneman/dp/0141033576/">
                <span class="a-size-small a-color-base">Taschenbuch</span>
                <span class="tmmAjaxLoading" id="tmmSpinnerDiv_4" style="display: none"></span></a>
            
            """
                        
            kindle = other_editions.find_next('span', class_='a-size-small a-color-base', string='Kindle')
                        
            kindle_price_object = kindle.find_next('span', class_='a-size-small a-color-price')

            kindle_price = get_price_from_bs4_object(kindle_price_object)
                        
            self.kindle_price = kindle_price

        except:
            print('kindle price not found')

                
#url = f'https://www.amazon.de/dp/3570103501'
#id = '3570103501'
#id = '0374275637'
#id = '0393320928'
#amazon_product_page = AmazonProductPage(id)
#print(amazon_product_page.product_price)
#print(amazon_product_page.product_seller_infos)
#print(amazon_product_page.versand_durch_amazon)
#print(amazon_product_page.kindle_edition)
#print(amazon_product_page.title)
#print(amazon_product_page.kindle_price)
#print(amazon_product_page.check_edition())