""" A class that can be used to represent a database of book deals """

import pandas as pd
import numpy as np

from datetime import datetime
from pandas import DataFrame, Series

from book import Book
from book_db import BookDatabase
from book_prices_db import BookPricesDatabase
from amazon_product_page import AmazonProductPage
from style import Style
from html_tools import HTMLTools

from open_url_in_safari import open_url_in_safari


class BookDealsDatabase():
    """ A class representing a database of book deals """

    def __init__(self, db_infos):
        
        self.db_infos = db_infos
        self.book_deals_db_path = db_infos.relative_paths.book_deals
        #self.book_prices_db_path = db_infos.relative_paths.book_prices

        # BookPricesDatabase
        self.book_prices_db = BookPricesDatabase(db_infos)
        self.book_prices_db.df = self.book_prices_db.df[['title', 'format', 'price', 'used_price', 'average_price', 'average_price_last_week', 'lowest_price', 'kindle_price']]
        
        # create a DataFrame with the latest date from BookPricesDatabase
        self.book_prices_db_last_date = None

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
        #self.calculate_difference_price_and_target_price()
        #self.calculate_percent_from_price_and_target_price()
        self.calculate_difference_from_price_and_average_price()
        self.calculate_difference_from_price_and_average_price_last_week()
        
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

    
    #def change_variables(self):
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
    
    
    def calculate_difference_from_price_and_average_price_last_week(self):
        price =  self.book_prices_db_last_date.loc[ : , 'price'].astype(float)
        average_price_last_week = self.book_prices_db_last_date.loc[ : , 'average_price_last_week'].astype(float)
        difference = price - average_price_last_week
        pattern_calculate_difference = difference
        self.book_prices_db_last_date.loc[ : , 'diff_avg_price_last_week'] = pattern_calculate_difference
        
    
    def create_deals_of_the_day(self):
        """ Create a DataFrame with the deals of the day """

        self.deals_of_the_day = self.book_prices_db_last_date

    
    def create_html_report(self):

        df = self.deals_of_the_day
        
        # apply goes through every row (x) and use x.name for getting the id
        #df['url'] = df.apply(lambda x: f'https://www.amazon.de/dp/{x.name[1]}', axis=1)
        
        # apply goes through every row (x) and builds a link for the title (x[0] with the amazon id (x.name[1])
        df['title'] = df.apply(lambda x: f'<a href="https://www.amazon.de/dp/{x.name[1]}">{x[0]}</a><code style="display:block">{x.name[1]}</code>', axis=1)

        #df = df[df['pct_target_price'] < 0].sort_values('pct_target_price')
                
        # not used anymore
        #df_price_diff = df[df['diff_avg_price'] < -1.49].sort_values('diff_avg_price')
        
        #price_diff_pct = df['diff_avg_price'].astype(float) / df['price'].astype(float)
        df_price_diff_pct = df[df['diff_avg_price'].astype(float) / df['average_price'].astype(float) < -0.10].sort_values('diff_avg_price')
        
        #df = df[df['pct_target_price'] < 10]
        
        # not used anymore
        #df_price_diff_last_week = df[df['diff_avg_price_last_week'] < -1.49].sort_values('diff_avg_price_last_week')
        
        #df3 = df[df['price'].astype(float) < 10]

        df_kindle_price = df[df['kindle_price'].astype(float) < 4].sort_values('kindle_price')

        # maybe too complex?
        prices50 = (df['price'].astype(float) > 50) & (df['diff_avg_price'].astype(float) < -10)
        prices40 = ((df['price'].astype(float) > 30) & (df['price'].astype(float) <= 40)) & (df['diff_avg_price'].astype(float) < -5)
        prices30 = ((df['price'].astype(float) > 20) & (df['price'].astype(float) <= 30)) & (df['diff_avg_price'].astype(float) < -5)
        prices20 = ((df['price'].astype(float) > 10) & (df['price'].astype(float) <= 20)) & (df['diff_avg_price'].astype(float) < -2)
        prices10 = (df['price'].astype(float) <= 10) & (df['diff_avg_price'].astype(float) < -1)
        
        """

        price_g_50 = df['price'] > 50     

        price_g_30 = df['price'] > 30
        price_g_20 = df['price'] > 20
        price_g_10 = df['price'] > 10

        price_l_40 = df['price'] <= 40
        price_l_30 = df['price'] <= 30
        price_l_20 = df['price'] <= 20

        prices50 = (price_u_50) & (df['diff_avg_price'] < -10) 
        
        prices40 = ((price_g_30) & (price_l_40)) & (df['diff_avg_price'] < -5)
        prices30 = ((price_g_20) & (price_l_30)) & (df['diff_avg_price'] < -5)
        prices20 = ((price_g_10) & (price_l_20)) & (df['diff_avg_price'] < -2)
        
        prices10 = (df['price'] <= 10) & (df['diff_avg_price'] < -1)
        
        """

        df_prices = df[prices50 | prices40 | prices30 | prices20 | prices10]

        def change_names(df):
        
            names = {
                'title':'Title',
                'format':'Format', 
                'price':'Price', 
                'used_price':'Used', 
                'average_price':'Ø', 
                'average_price_last_week':'Ø 7',
                'diff_avg_price':'Ø diff',
                'diff_avg_price_last_week':'Ø diff 7',
                'lowest_price':'Lowest',
                'kindle_price':'Kindle'
                }

            df = df.rename(columns=names)
            df = df[['Title', 'Format', 'Price', 'Ø', 'Ø diff', 'Ø 7', 'Ø diff 7', 'Lowest', 'Used', 'Kindle']]

            return df

        # html style
        style_functions = Style()
                

        df_price_diff_pct = change_names(df_price_diff_pct)
        
        html2 = df_price_diff_pct.style.\
            set_table_attributes('class="table table-sm  align-middle"').\
            set_table_styles([{'selector': 'th','props': [('background-color', 'yellow'), ('text-align', 'right') ]}]).\
            set_properties(subset=['Format','Price', 'Ø', 'Ø diff', 'Ø 7', 'Ø diff 7', 'Lowest', 'Used', 'Kindle'], **{'width': '80px'}).\
            set_properties(subset=['Title'], **{'width': '700px'}).\
            applymap(style_functions.align_text).\
            apply(style_functions.highlight_if_lowest, axis=None, subset=['Price', 'Lowest']).\
            hide_index().\
            render()

        
        df_kindle_price = change_names(df_kindle_price)
        
        html4 = df_kindle_price.style.\
            set_table_attributes('class="table table-sm  align-middle"').\
            set_table_styles([{'selector': 'th','props': [('background-color', 'yellow'), ('text-align', 'right') ]}]).\
            set_properties(subset=['Format','Price', 'Ø', 'Ø diff', 'Ø 7', 'Ø diff 7', 'Lowest', 'Used', 'Kindle'], **{'width': '80px'}).\
            set_properties(subset=['Title'], **{'width': '700px'}).\
            applymap(style_functions.align_text).\
            hide_index().\
            render()
        
        df_prices = change_names(df_prices)

        html5 = df_prices.style.\
            set_table_attributes('class="table table-sm  align-middle"').\
            set_table_styles([{'selector': 'th','props': [('background-color', 'yellow'), ('text-align', 'right') ]}]).\
            set_properties(subset=['Format','Price', 'Ø', 'Ø diff', 'Ø 7', 'Ø diff 7', 'Lowest', 'Used', 'Kindle'], **{'width': '80px'}).\
            set_properties(subset=['Title'], **{'width': '700px'}).\
            applymap(style_functions.align_text).\
            apply(style_functions.highlight_if_lowest, axis=None, subset=['Price', 'Lowest']).\
            hide_index().\
            render()
        
        
        html_tools = HTMLTools()

        html2 = html_tools.create_html_element('b', 'Percent from Difference from Average (0.10)') + html2
        html4 = html_tools.create_html_element('b', 'Kindle Price') + html4
        html5 = html_tools.create_html_element('b', 'Difference from Average depending on Price') + html5


        
        html = html2 + html4 + html5

        

        div_main_content = html_tools.create_html_element('div', html, classes='col-8')
        div_space = html_tools.create_html_element('div', '', classes='col-2')
        div_row = html_tools.create_html_element('div', div_space + div_main_content + div_space, classes='row')
        div_container = html_tools.create_html_element('div', div_row, classes='table-responsive')
        
        html_page = html_tools.create_html_page(html)


        with open(self.db_infos.relative_paths.book_deals_report_html, 'w', encoding='utf-8') as html_report:
            html_report.write(html_page)
        
        open_url_in_safari(self.db_infos.absolute_paths.book_deals_report_html)


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


from db_infos import choose_db

#book_deals_db = BookDealsDatabase(choose_db('real_deal'))
#book_deals_db.add_variable_to_db('deal')
#book_deals_db.run()
#book_deals_db.get_deals_from_db()
#book_deals_db.create_html_report()
#print(book_deals_db.length_unique_dates)
#print(book_deals_db.book_prices_db_last_date)
#print(book_deals_db.calculate_difference_price_and_target_price())
#print(book_deals_db.calculate_percent_price_and_target_price)
#book_deals_db.create_html_report()
#book_deals_db.calculate_difference_from_price_and_average_price_last_week()