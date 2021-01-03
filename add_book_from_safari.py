from get_id_from_url import get_id_from_url
from get_url_from_safari import get_url_from_safari
from settings import book_db_path

from book_db import BookDatabase


def add_book_from_safari():
    """ Add book to a database from Safari """

    url = get_url_from_safari()
    id = get_id_from_url(url)

    book_db = BookDatabase(book_db_path)

    book_db.add_entry_to_book_db(id)
    book_db.write_csv()

add_book_from_safari()






    