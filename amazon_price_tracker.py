from book_prices_db import BookPricesDatabase
from book_deals_db import BookDealsDatabase

from settings import book_deals_db_path 
from settings import book_prices_db_path 
from settings import book_deals_report_html_path

book_prices_db = BookPricesDatabase(book_prices_db_path)
book_prices_db.run()

book_deals_db = BookDealsDatabase(book_deals_db_path)
book_deals_db.run()
