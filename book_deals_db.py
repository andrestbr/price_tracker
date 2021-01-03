""" A class that can be used to represent a database of book deals """

import pandas as pd
import numpy as np

from datetime import datetime
from pandas import DataFrame, Series

from book import Book
from book_db import BookDatabase
from book_prices_db import BookPricesDatabase
from amazon_product_page import AmazonProductPage

from open_url_in_safari import open_url_in_safari

from settings import book_deals_db_path 
from settings import book_prices_db_path 
from settings import book_deals_report_html_path
from settings import book_deals_report_html_file_path


class BookDealsDatabase():
    """ A class representing a database of book deals """

    def __init__(self, book_deals_db_path):
        
        self.book_deals_db_path = book_deals_db_path
        self.book_prices_db_path = book_prices_db_path

        # BookPricesDatabase
        self.book_prices_db = BookPricesDatabase(book_prices_db_path)
        self.book_prices_db.df = self.book_prices_db.df[['title', 'format', 'price', 'target_price', 'used_price', 'average_price']]
        
        # create a DataFrame with the latest date from BookPricesDatabase
        self.book_prices_db_last_date = None

        #self.df.loc[ : , 'price'] = self.df.loc[ : , 'price'].astype(float)
        #self.book_prices_db_last_date[['price', 'target_price']] = self.book_prices_db_last_date[['price', 'target_price']].astype(float)
        #print(self.book_prices_db_last_date.loc[ : , 'price'])
       
        # BookDealsDatabase
        self.date = datetime.now().strftime('%Y-%m-%d')

        self.df = pd.read_csv(self.book_deals_db_path, header=0, dtype='str')

        # set MultiIndex to date and id
        self.df = self.df.set_index(['date', 'id'])  

        self.unique_dates = self.df.index.get_level_values('date').unique()
        self.unique_ids = self.df.index.get_level_values('id').unique()
        
        self.length_unique_dates = len(self.unique_dates)
        self.last_date = None

        # daily_deals
        self.deals_of_the_day = None

        self.get_last_date_from_db()

        self.create_df_last_date()
        #self.change_variables()
        self.calculate_difference_price_and_target_price()
        self.calculate_percent_from_price_and_target_price()
        self.calculate_difference_from_price_and_average_price()
        
        self.create_deals_of_the_day()

    
    def check_date(self, date):
        """ Check if a given date is already in the database """

        if date in self.unique_dates:
            return True
        
        return False

    
    def get_last_date_from_db(self):
        """ Get last entry stored in the database """

        if self.length_unique_dates > 0:
            self.last_date = self.unique_dates[-1]

    
    def create_df_last_date(self):
        
        last_date_pattern = self.book_prices_db.df.loc[self.book_prices_db.last_date : self.book_prices_db.last_date]

        self.book_prices_db_last_date = last_date_pattern.copy()

    
    def change_variables(self):
        print()
        #book_prices_db = BookPricesDatabase(book_prices_db_path)
        #df_last_date = book_prices_db.df.loc[book_prices_db.last_date : book_prices_db.last_date]
        #df_last_date.loc[ : , 'price'] = df_last_date.loc[ : , 'price'].astype(float)

        #df = self.book_prices_db_last_date
        #df[['price', 'target_price']] = self.df[['price', 'target_price']].astype(float, copy=False)
        #self.book_prices_db_last_date = df

            
    def log_db(self):
        """ Log database """
        
        self.df.to_csv(f'log/amz_book_deals_db_{self.date}.csv')

    
    def calculate_difference_price_and_target_price(self):
        """ Compare price and target price from BookPricesDatabase """

        price = self.book_prices_db_last_date.loc[ : , 'price'].astype(float)
        target_price = self.book_prices_db_last_date.loc[ : , 'target_price'].astype(float)
        difference = price - target_price

        pattern_calculate_difference = difference
        self.book_prices_db_last_date.loc[ : , 'diff_target_price'] = pattern_calculate_difference 

    
    def calculate_percent_from_price_and_target_price(self):
        """ Calculate the difference in percent between price and target price """

        price =  self.book_prices_db_last_date.loc[ : , 'price'].astype(float)
        target_price = self.book_prices_db_last_date.loc[ : , 'target_price'].astype(float)
        difference = price - target_price
        pct = difference / price * 100
        pct_rounded = round(pct, 2)
        pattern_calculate_percent = pct_rounded
        self.book_prices_db_last_date.loc[ : , 'pct_target_price'] = pattern_calculate_percent


    def calculate_difference_from_price_and_average_price(self):
        price =  self.book_prices_db_last_date.loc[ : , 'price'].astype(float)
        average_price = self.book_prices_db_last_date.loc[ : , 'average_price'].astype(float)
        difference = price - average_price
        pattern_calculate_difference = difference
        self.book_prices_db_last_date.loc[ : , 'diff_avg_price'] = pattern_calculate_difference
    

    def create_deals_of_the_day(self):
        """ Create a DataFrame with the deals of the day """

        self.deals_of_the_day = self.book_prices_db_last_date

    
    def create_html_report(self):

        #if self.df_deals_of_the_day.empty:
        #    print('no deals stored')
        #    return None

        df = self.deals_of_the_day
        
        # apply goes through every row (x) and use x.name for getting the id
        df['url'] = df.apply(lambda x: f'https://www.amazon.de/dp/{x.name[1]}', axis=1)


        #df = df[df['pct_target_price'] < 0].sort_values('pct_target_price')
        
        df = df[df['diff_avg_price'] < -0.99].sort_values('diff_avg_price')
        #df = df[df['pct_target_price'] < 10]
        
    
        df.to_html(book_deals_report_html_path, index=False, render_links=True)

        open_url_in_safari(book_deals_report_html_file_path)


    def add_variable_to_db(self, variable):
        """ Add new variable to db """

        # Add a new variable (Merkmal, Spalte) to the database 
        self.df[variable] = np.nan


    def write_csv(self):
        """ Write db as a csv file """

        self.log_db()
        
        # consider using na_rep='NA'
        self.df.to_csv(self.book_deals_db_path)

    
    def run(self):
        #self.write_csv()
        self.create_html_report()


#book_deals_db = BookDealsDatabase(book_deals_db_path)
#book_deals_db.add_variable_to_db('deal')
#book_deals_db.run()
#book_deals_db.get_deals_from_db()
#book_deals_db.create_html_report()
#print(book_deals_db.length_unique_dates)
#print(book_deals_db.book_prices_db_last_date)
#print(book_deals_db.calculate_difference_price_and_target_price())
#print(book_deals_db.calculate_percent_price_and_target_price)
#book_deals_db.create_html_report()