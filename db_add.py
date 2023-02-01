import os
import sqlite3
import logging
from datetime import datetime

log_filename = "pdf_tracker_{}.log".format(datetime.now().strftime("%Y-%m-%d"))
logging.basicConfig(filename=log_filename, level=logging.INFO)

DB_NAME = 'pdf_tracker.db'
TABLE_NAME = 'auftraege'
pdf_folder = '/home/PDF-Tracker/'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS auftraege (fa_auftr text, fa_artikel text, fa_start text, fa_ende text)''')
    conn.commit()
    return conn

def close_db(conn):
    conn.commit()
    conn.close()

def insert_to_db(conn, file_name):
    c = conn.cursor()
    query = "INSERT INTO auftraege (fa_auftr, fa_artikel, fa_start, fa_ende) VALUES (?,?,?,?)"
    c.execute(query, (file_name, "unknown", "2023-02-01", "2023-02-01"))

def delete_from_db(conn, file_name):
    c = conn.cursor()
    query = "DELETE FROM auftraege WHERE fa_auftr=?"
    c.execute(query, (file_name,))

def check_pdf_files():
    conn = init_db()
    c = conn.cursor()
    c.execute("SELECT fa_auftr from auftraege")
    db_files = set(row[0] for row in c.fetchall())
    folder_files = set(f for f in os.listdir(pdf_folder) if f.endswith('.pdf'))

    for file_name in folder_files - db_files:
        insert_to_db(conn, file_name)
        logging.info("File '{}' inserted to db".format(file_name))

    for file_name in db_files - folder_files:
        if os.path.exists(os.path.join(pdf_folder, file_name)):
            continue
        delete_from_db(conn, file_name)
        logging.info("File '{}' deleted from db".format(file_name))

    close_db(conn)

if __name__ == '__main__':
    while True:
        check_pdf_files()
