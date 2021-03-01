""" A class that can be used to represent a database of book prices """

import pandas as pd
import numpy as np

import random
import time

from datetime import datetime
from pandas import DataFrame, Series

from book import Book
from book_db import BookDatabase
from amazon_product_page import AmazonProductPage


class BookPricesDatabase():
    """ A class representing a database of book prices """

    def __init__(self, db_infos):
        
        # BookDatabase
        self.book_db = BookDatabase(db_infos.relative_paths.books)
        
        # BookPricesDatabase
        self.book_prices_db_path = db_infos.relative_paths.book_prices
        self.date = datetime.now().strftime('%Y-%m-%d')

        self.df = pd.read_csv(self.book_prices_db_path, header=0, dtype='str')

        # set MultiIndex to date and id
        self.df = self.df.set_index(['date', 'id'])  

        self.unique_dates = self.df.index.get_level_values('date').unique()
        self.unique_ids = self.df.index.get_level_values('id').unique()

        self.length = len(self.unique_ids)
        self.last_date = None

        self.unique_ids_last_date = None
        self.unique_ids_for_today = None

        self.min_waiting_time_between_ids = 7
        self.max_waiting_time_between_ids = 10

        self.waiting_time_between_buckets = 600
        
        self.runtime = None

        self.counter_id = 0
        self.counter_price_not_found = 0
        self.counter_kindle_not_found = 0
        self.buckets_to_crawl_today = None
        self.buckets_crawled_today = None

        self.get_last_date_from_db()

        self.unique_ids_last_date = self.get_ids_from_date(self.last_date)
        self.unique_ids_for_today = self.get_ids_from_date(self.date)
        
        # check if necessary 
        #self.df['price'].astype(float, copy=False)
    

    def log_db(self):
        """ Log database """
        
        self.df.to_csv(f'log/amz_book_prices_db_{self.date}.csv')

    
    def check_date(self, date):
        """ Check if a given date is already in the database """

        if date in self.unique_dates:
            return True
        
        return False

    
    def check_id_in_date(self, id, date):
        """ Check if an id is stored for a given date """

        if self.check_date(date):
            
            grouped = self.df.groupby(level='date')
            ids = grouped.get_group(date).index.get_level_values('id').unique()

            if id in ids:
                return True
        
        return False    

    
    def check_id(self, id):
        """ Check if a given id is already in the database """

        if id in self.unique_ids:
            #print('an id for this date is already in the database')
            return True
        
        return False


    def check_bucket_of_ids_in_date(self, bucket, date):
        """ check if a given group of ids is stored for a given date """

        for id in bucket:
            print(id)
            if not self.check_id_in_date(id, date):
                return False
            
            self.update_counter_id()
        
        print('id bucket already in date')
        
        return True  


    def get_last_date_from_db(self):
        """ Get last entry stored in the database """

        if self.length > 0:
            self.last_date = self.unique_dates[-1]
        

    def calculate_average_over_time(self, id):
        """ Calculate price average over time for a given id """

        if not self.check_id(id):
            print('id for price average not found')
            return np.nan

        grouped = self.df['price'].astype(float).groupby(level='id')
        prices = grouped.get_group(id)
        
        # TODO: find more elegant way to deal with no entries in prices
        average_price = np.nan
        
        if prices.any():
            average_price = prices.mean().round(2)

        return average_price

    
    def calculate_average_last_week(self, id):
        """ Calculate price average of the last week for a given id """

        if not self.check_id(id):
            print('id for price average not found')
            return np.nan

        grouped = self.df['price'].astype(float).groupby(level='id')
        prices = grouped.get_group(id)

        # slice from all prices in the db (10 days)
        prices_last_entries = prices[-10: ] 
        
        average_price_last_week = np.nan
        
        if prices.any():
            average_price_last_week = prices_last_entries.rolling(window=7, min_periods=1).mean().round(2)[-1]
        
        # TODO: find more elegant way to deal with no entries in prices
        
        return average_price_last_week
        

    def calculate_lowest_price(self, id):
        """ Calculate lowest price in the db for a given id """

        if not self.check_id(id):
            print('id for lowest price not found')
            return np.nan

        grouped = self.df['price'].astype(float).groupby(level='id')
        prices = grouped.get_group(id)

        lowest_price = np.nan

        if prices.any():
            lowest_price = prices.min()

        return lowest_price
    
    
    def add_entry_to_book_prices_db(self, book_information):
        """ Add book information to the database """

        id = book_information.name        
        
        if self.check_id_in_date(id, self.date):
            print('id already found for this date')
            return None

        # initialize instance from amazon product page. get price as an attribute of the class 
        amazon_product_page = AmazonProductPage(id)
        
        """ 
        Series consisting of the information stored in book_information, prices and average price
        The name of the Series is the date (self.date) and the id (book_information.name), 
        which will be used as index for an entry in the DataFrame
        """

        price = amazon_product_page.product_price
        average_price = self.calculate_average_over_time(id)
        average_price_last_week = self.calculate_average_last_week(id)
        lowest_price = self.calculate_lowest_price(id)
        kindle_price = amazon_product_page.kindle_price
        
        used_price = None

        entry_for_book_prices_db = Series({
            'title': book_information['title'],
            'format': book_information['format'],
            'target_price': book_information['target_price'],
            'price': price,
            'used_price': used_price,
            'average_price': average_price,
            'average_price_last_week': average_price_last_week,
            'lowest_price': lowest_price,
            'kindle_price': kindle_price
        }, name=(self.date, book_information.name))
        
        self.df = self.df.append(entry_for_book_prices_db)
        
        waiting_time = random.randrange(7,10)
        print(f'waiting {waiting_time} seconds')
        time.sleep(waiting_time)

    
    def crawl_all_id_buckets(self):
                    
        print(f'number of ids: {len(self.book_db.unique_ids)}')

        for bucket in self.book_db.id_buckets:

            
            if self.check_bucket_of_ids_in_date(bucket, self.date):
                continue
   
            self.crawl_ids(bucket)
            self.write_csv()
            print(f'waiting {self.waiting_time_between_buckets / 60} minutes')
            time.sleep(self.waiting_time_between_buckets)
            
    
    def crawl_ids(self, bucket):

        for id in bucket:
            print(id)
            book_information = self.book_db.get_book_information_from_book_db(id)
            self.add_entry_to_book_prices_db(book_information)
            self.update_counter_id()

    
    def update_counter_id(self):
        self.counter_id += 1
        print(f'{self.counter_id} from {len(self.book_db.unique_ids)}')
    
    
    #def crawl_book_db(self):

        #book_db = BookDatabase(book_db_path)
        #length_book_db = len(book_db.unique_ids)
        #self.calculate_runtime(length_book_db)

        #try:
        #    for id in book_db.unique_ids:
        #        print(id)
        #        book_information = book_db.get_book_information_from_book_db(id)
        #        self.add_entry_to_book_prices_db(book_information)
        #except:
        #    print('writing db')
        #    self.write_csv()
                    
    
    def add_variable_to_db(self, variable):
        """ Add new variable to db """

        # Add a new variable (Merkmal, Spalte) to the database 
        self.df[variable] = np.nan

        # Add a new variable with groupby
        #self.df['lowest_price'] = self.df['price'].astype(float).groupby(level='id').transform('min')
        
        # check with print before writing file
        #self.write_csv()
        

    def delete_variable_from_db(self, variable):
        """ Delete variable from db """

        self.df = self.df.drop(variable, axis=1)
        
        # check with print before writing file
        #self.write_csv()
        
    
    def calculate_runtime(self):
        """ Calculate runtime """

        if not self.book_db.length:
            print('no ids found in database')
            return None

        runtime_ids = self.book_db.length * self.max_waiting_time_between_ids
        runtime_buckets = len(self.book_db.id_buckets) * self.waiting_time_between_buckets
        self.runtime = runtime_ids + runtime_buckets

        print(f'length: {self.book_db.length}')
        print(f'runtime: {self.runtime}')
        print(f'runtime in minutes: {self.runtime / 60}')
        print(f'runtime in hours: {self.runtime / 60 / 60}')

        # TODO: consider time library
    

    def write_csv(self):
        """ Write db as a csv file """

        self.log_db()
        
        # consider using na_rep='NA'
        self.df.to_csv(self.book_prices_db_path)

    
    def delete_book_from_book_prices_db(self, id):
        """ Delete book from the database """

        if not self.check_id(id):
            print('id not found in the db')
            return None
        
        # also consider drop entries by creating a dataframe without the matching ids
        # df = df[df.id != id]
        #        
        self.df = self.df.drop(index=id, level=1)


    def get_ids_from_date(self, date):
        """ Get all ids from a DataFrame given a date """

        if self.df.loc[date : date].empty:
            return None
    
        ids = self.df.loc[date : date].index.get_level_values('id').unique()

        return ids

    
    def run(self):

        start_time = time.time()
        self.calculate_runtime()
        
        self.crawl_all_id_buckets()

        print(f'runtime: {time.time() - start_time}')


from db_infos import choose_db

#book_prices_db = BookPricesDatabase(choose_db('real_deal'))
#book_prices_db.run()
#print(book_prices_db.calculate_average_over_time('3570103501'))
#book_prices_db.add_entry_to_book_prices_db('3570103501')
#book_prices_db.delete_book_from_book_prices_db('3570103501')
#book_prices_db.add_variable_to_db('')
#book_prices_db.calculate_runtime()
#print(book_prices_db.length)
#print(book_prices_db.unique_ids_last_date)
#print(book_prices_db.unique_ids_for_today)
#print(book_prices_db.get_ids_from_date(book_prices_db.date))
#book_prices_db.check_bucket_of_ids_in_date(book_prices_db.book_db.id_buckets[0], book_prices_db.date)
#book_prices_db.calculate_average_last_week('1509528601')
#book_prices_db.calculate_lowest_price('1633698122')
#print(book_prices_db.run())
#book_prices_db.delete_variable_from_db('target_price')