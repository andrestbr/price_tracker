from book_prices_db import BookPricesDatabase
from book_deals_db import BookDealsDatabase

from settings import real_deal_paths

book_prices_db = BookPricesDatabase(real_deal_paths)
book_prices_db.run()

book_deals_db = BookDealsDatabase(real_deal_paths)
book_deals_db.run()
