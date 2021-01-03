""" A class that can be used to represent a book from goodreads """

import requests
import bs4

from settings import key


class BookGoodreads():
    """ A class representing a book from goodreads """

    def __init__(self, amz_id):
        
        self.amz_id = amz_id
        self.id = None

        self.url = f'https://www.goodreads.com/book/isbn/{self.amz_id}'
        
        self.title = None
        self.author = None
        self.publisher = None
        self.isbn13 = None
        self.publication_year = None  
        self.pages = None
        self.format = None

        self.missing_information = None
        
        # call function to assign a value to id
        self.get_id(self.amz_id)

        # call function to assign values to book information
        self.get_book_information()


    def get_id(self, isbn):
        """ Get a goodreads id using a book isbn """

        url = 'https://www.goodreads.com/book/isbn_to_id'
        r = requests.get(url, params={'key':key, 'isbn':isbn})

        self.id = r.text

    
    def get_book_information(self):
        """ Get book information from goodreads"""
      
        r = requests.get(self.url, params={'key':key, 'format':'xml'})   
        soup = bs4.BeautifulSoup(r.text, 'xml')

        # TODO: more elegant way
        if soup.text == 'Page not found':
            
            print(f'cannot retrieve information from goodreads for id {self.amz_id}')
            print(f'error message: {soup.text}')
            
            self.missing_information = True
            return None

        book = soup.find('book')

        self.title = book.find('title').get_text(strip=True)
        self.author = book.find('author').find('name').get_text(strip=True)
        self.publisher = book.find('publisher').get_text(strip=True)
        self.isbn13 = book.find('isbn13').get_text(strip=True)
        self.publication_year = book.find('publication_year').get_text(strip=True)   
        self.pages = book.find('num_pages').get_text(strip=True)
        self.format = book.find('format').get_text(strip=True)
                

#bg = BookGoodreads('0374275637')
#bg = BookGoodreads('')

#print(bg.amz_id)
#print(bg.id)
#print(bg.author)


