""" A class that can be used to represent a book database """

import pandas as pd
import numpy as np

from datetime import datetime

from book import Book


class BookDatabase():
    """ A class representing a book database """


    def __init__(self, book_db_path):
        
        self.book_db_path = book_db_path  
        self.date = datetime.now().strftime('%Y-%m-%d')

        self.df = pd.read_csv(self.book_db_path, header=0, dtype='str')

        # set index to id
        self.df = self.df.set_index('id')  

        self.unique_ids = self.df.index.unique()
        self.length = len(self.unique_ids)
        
        self.id_buckets = None

        self.id_buckets = self.divide_list_in_buckets(self.unique_ids, 10)
        

    def log_db(self):
        """ Log database """
        
        self.df.to_csv(f'log/amz_book_db_{self.date}.csv')

    
    def check_id(self, id):
        """ Check if a given id is already in the database """

        if id in self.unique_ids:
            return True
        
        return False

    
    def get_book_information_from_book_db(self, id):
        """ Get book information (row) stored for a given id """

        return self.df.loc[id] 


    def write_csv(self):
        """ Write db as a csv file """

        self.log_db()
        self.df.to_csv(self.book_db_path)
        
    
    def add_entry_to_book_db(self, id):
        """ Add book to database """
            
        if self.check_id(id):
            print('id already in the db')
            return None
        
        b = Book(id)
        
        # create variable for date added
        date_added = self.date
        
        self.df.loc[id] = [
            b.title, 
            b.format, 
            date_added, 
            b.isbn13, 
            b.publication_year, 
            b.publisher, 
            b.pages, 
            b.target_price
            ]
        
        return True

    
    def divide_list_in_buckets(self, a_list, length):
        """ Divide a given list in groups """

        return np.array_split(a_list, length)

    
    def delete_book_from_db(self, id):
        """ Delete book from the database """

        if not self.check_id(id):
            print('id not found in the db')
            return None
        
        self.df = self.df.drop(index=id)

        return True
        
                
#from settings import book_db_path

#book_db = BookDatabase(book_db_path)
#book_db.add_book_to_db('0374275637')
#book_db.add_book_to_db('3570103501')
#book_db.add_book_to_db('')
#book_db.get_book_information_from_book_db('3570103501')


#book_db.delete_book_from_db('0374275637')

#bg = BookGoodreads('0374275637')
#bg = BookGoodreads('')

#print(len(book_db.unique_ids))
#print(book_db.id_buckets)

#print(bg.amz_id)
#print(bg.id)
#print(bg.author)


# https://stackoverflow.com/questions/13148429/how-to-change-the-order-of-dataframe-columns
# https://stackoverflow.com/questions/2052390/manually-raising-throwing-an-exception-in-python

# https://realpython.com/introduction-to-python-generators/