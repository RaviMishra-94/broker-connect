import json
import requests
import sqlite3
import os
import pandas as pd

from logzero import logger

script_dir = os.path.dirname(os.path.abspath(__file__))
_db_filename = os.path.join(script_dir, '../scrip_master.db')
csv_filename = os.path.join(script_dir, "angelOne_scrip.csv")
url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
_filename = csv_filename

#SQL Queries
TABLE_NAME = "angelOne_scrip_data"
CREATE_TABLE_QUERY = '''CREATE TABLE IF NOT EXISTS {tableName}(
                    Token TEXT,
                    Symbol TEXT,
                    Name TEXT,
                    Expiry TEXT,
                    StrikePrice TEXT,
                    LotSize TEXT,
                    InstrumentType TEXT,
                    Segment TEXT,
                    TickSize TEXT
                    );'''.format(tableName=TABLE_NAME)

INSERT_DATA_QUERY = 'INSERT INTO {tableName} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);'.format(tableName=TABLE_NAME)

CLEAR_TABLE_QUERY = 'DELETE FROM {tableName};'.format(tableName=TABLE_NAME)


def download_csv_from_url():
    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Write the content of the response to a local file
        with open(_filename, 'wb') as file:
            file.write(response.content)
        print(f"CSV file downloaded successfully as '{_filename}'")
    else:
        print("Failed to download CSV file")


def read_csv(file_path):
    with open(file_path, 'r') as file:
        line = file.readline().strip()
        if line:
            objects = json.loads(line)
        else:
            objects = []
    return objects


def _create_table(cursor, query):
    cursor.execute(query)


def _insert_data(cursor, query, data):
    cursor.executemany(query, data)


def _clear_table(cursor, query):
    cursor.execute(query)


def _store_csv_to_sqlite(filenames: list, db_filename: str, clear_table_query: str, create_table_query: str,
                         insert_data_query: str):
    # Connect to SQLite database
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()

    try:
        _clear_table(cursor, clear_table_query)
    except Exception as e:
        logger.error("Error in clearing icici scrip table due to: {e}".format(e=e))
    # Create table if not exists
    _create_table(cursor, create_table_query)

    for filename in filenames:
        # Read CSV file into a DataFrame
        df = read_csv(filename)

        data = []
        for obj in df:
            data.append((obj['token'], obj['symbol'], obj['name'], obj['expiry'], obj['strike'], obj['lotsize'],
                         obj['instrumenttype'], obj['exch_seg'], obj['tick_size']))

        # Insert data into the SQLite database
        _insert_data(cursor, insert_data_query, data)
        print(f"Inserted data from {filename} into SQLite database.")

    # Commit changes and close connection
    conn.commit()
    conn.close()


def store_csv_to_sqlite():
    _store_csv_to_sqlite([_filename], _db_filename, CLEAR_TABLE_QUERY, CREATE_TABLE_QUERY, INSERT_DATA_QUERY)


def download_store_delete_csv():
    """
    Download the CSV files from the URL, store the data in SQLite database and delete the CSV files.
    """
    download_csv_from_url()
    store_csv_to_sqlite()
    os.remove(_filename)


def get_token_id_from_symbol(symbol: str, exchange: str):
    """
    Get the token id from the symbol and exchange
    :param symbol:
    :param exchange: NSE BSE NFO CDS MCX NCDEX BFO

    :return token_id:
    """

    conn = sqlite3.connect(_db_filename)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT Token FROM angelOne_scrip_data WHERE Symbol like ? AND Segment = ?",
                       [symbol, exchange])
    except Exception as e:
        logger.error("Error in fetching data from db due to: {e}".format(e=e))

    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]
    else:
        return None
    
def get_token_and_exchange_from_symbol(symbol):
    """
    Get the token id from the sytmbol and exchange
    :param symbol:
    :param exchange:
        NSE
        BSE
        NFO
        CDS
        MCX
        NCDEX
        BFO
    :return token_id:
    """

    conn = sqlite3.connect(_db_filename)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT Token, Segment FROM angelOne_scrip_data WHERE Symbol = ?", (symbol,))
    except:
        download_csv_from_url()
        store_csv_to_sqlite()
        cursor.execute("SELECT Token, Segment FROM angelOne_scrip_data WHERE Symbol = ?", (symbol,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row
    else:
        return None

if __name__ == "__main__":
    # download_csv_from_url()
    # store_csv_to_sqlite()
    # download_store_delete_csv()
    print(get_token_id_from_symbol("TAPARIA", "BSE"))
    print(get_token_id_from_symbol("SBIN-EQ", "NSE"))
    print(get_token_id_from_symbol("NIFTY31OCT2424700CE", "NFO"))