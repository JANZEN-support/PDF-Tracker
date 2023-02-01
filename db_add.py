"""
Der Code überwacht den Ordner /home/PDF-Tracker und fügt neue PDF-Dateien hinzu
oder entfernt gelöschte aus der Datenbank pdf_tracker.db.
Jede Aktion wird in einer Logdatei pro Tag geloggt.
"""
import os
import sqlite3
import logging
from datetime import datetime

# Erstelle ein Log-File mit Datum im Namen
log_filename = "pdf_tracker_{}.log".format(datetime.now().strftime("%Y-%m-%d"))
logging.basicConfig(filename=log_filename, level=logging.INFO)

# Variablen für Datenbank- und Ordnernamen
DB_NAME = 'pdf_tracker.db'
TABLE_NAME = 'auftraege'
pdf_folder = '/home/PDF-Tracker/'

def init_db():
    """
    Erstelle eine Verbindung zur Datenbank und initialisiere die Tabelle,
    falls sie noch nicht existiert.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS auftraege (fa_auftr text, fa_artikel text, fa_start text, fa_ende text)''')
    conn.commit()
    return conn

def close_db(conn):
    """
    Speichere die Änderungen in der Datenbank und schließe die Verbindung.
    """
    conn.commit()
    conn.close()

def insert_to_db(conn, file_name):
    """
    Füge einen neuen Eintrag in die Datenbank hinzu.
    """
    c = conn.cursor()
    query = "INSERT INTO auftraege (fa_auftr, fa_artikel, fa_start, fa_ende) VALUES (?,?,?,?)"
    c.execute(query, (file_name, "unknown", "2023-02-01", "2023-02-01"))

def delete_from_db(conn, file_name):
    """
    Lösche einen Eintrag aus der Datenbank.
    """
    c = conn.cursor()
    query = "DELETE FROM auftraege WHERE fa_auftr=?"
    c.execute(query, (file_name,))

def check_pdf_files():
    """
    Überprüfe, ob es neue Dateien im Ordner gibt und füge sie in die Datenbank ein,
    falls sie noch nicht vorhanden sind. Überprüfe auch, ob gelöschte Dateien
    aus dem Ordner auch in der Datenbank gelöscht werden müssen.
    """
    conn = init_db()
    c = conn.cursor()
    c.execute("SELECT fa_auftr from auftraege")
    db_files = set(row[0] for row in c.fetchall())
    folder_files = set(f for f in os.listdir(pdf_folder) if f.endswith('.pdf'))

    # Die folgenden beiden Schleifen überprüfen, ob neue PDF-Dateien im Ordner hinzugefügt oder gelöscht wurden
    # und führen entsprechende Aktionen in der Datenbank durch.
    for file_name in folder_files - db_files:
        # Einfügen der neuen PDF-Datei in die Datenbank
        insert_to_db(conn, file_name)
        # Protokollierung des Einfügens in das Log-File
        logging.info("File '{}' inserted to db".format(file_name))

    for file_name in db_files - folder_files:
    
        # Überprüfen, ob die Datei im Ordner noch vorhanden ist
        if os.path.exists(os.path.join(pdf_folder, file_name)):
            continue
        # Löschen der Datei aus der Datenbank, falls sie nicht mehr im Ordner vorhanden ist
        delete_from_db(conn, file_name)
        # Protokollierung des Löschens in das Log-File
        logging.info("File '{}' deleted from db".format(file_name))

    # Schließen der Verbindung zur Datenbank
    close_db(conn)

# Überprüfen, ob das Script als Hauptprogramm ausgeführt wird
if __name__ == '__main__':
    # Endlosschleife, um ständig auf Veränderungen im Ordner zu überwachen
    while True:
        check_pdf_files()
