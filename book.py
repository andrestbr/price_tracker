""" A class that can be used to represent a book from amazon """

from book_goodreads import BookGoodreads


class Book():
    """ A class representing an amazon book """

    def __init__(self, id):
        """ Initialize attributes """
        self.id = id
        self.url = f'https://www.amazon.de/dp/{id}'

        # initialize instance from goodreads book
        self.book = BookGoodreads(self.id)

        self.title = self.book.title
        self.author = self.book.author
        self.publisher = self.book.publisher
        self.isbn13 = self.book.isbn13
        self.publication_year = self.book.publication_year  
        self.pages = self.book.pages
        self.format = self.book.format

        self.target_price = None

    
    def ask_target_price(self):
        """ Ask for a target price """
        
        target_price = input('enter target price: ')

        # TODO: control input

        self.target_price = target_price
        

#b = Book('0374275637')
#print(b.id)
#print(b.url)
#print(b.book.author)



    
        




