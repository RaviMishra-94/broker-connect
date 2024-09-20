import json
import requests
import sqlite3
import os
import pandas as pd
from logzero import logger

script_dir = os.path.dirname(os.path.abspath(__file__))
_db_filename = os.path.join(script_dir, '../scrip_master.db')
csv_filename = os.path.join(script_dir, "dhan_scrip.csv")
url = "https://images.dhan.co/api-data/api-scrip-master.csv"
_filename = csv_filename

# SQL Queries
TABLE_NAME = "dhan_scrip_data"
CREATE_TABLE_QUERY = '''CREATE TABLE IF NOT EXISTS {tableName} (
                    SEM_EXM_EXCH_ID TEXT,
                    SEM_SEGMENT TEXT,
                    SEM_SMST_SECURITY_ID TEXT,
                    SEM_INSTRUMENT_NAME TEXT,
                    SEM_EXPIRY_CODE TEXT,
                    SEM_TRADING_SYMBOL TEXT,
                    SEM_LOT_UNITS INTEGER,
                    SEM_CUSTOM_SYMBOL TEXT,
                    SEM_EXPIRY_DATE TEXT,
                    SEM_STRIKE_PRICE REAL,
                    SEM_OPTION_TYPE TEXT,
                    SEM_TICK_SIZE REAL,
                    SEM_EXPIRY_FLAG TEXT,
                    SEM_EXCH_INSTRUMENT_TYPE TEXT,
                    SEM_SERIES TEXT,
                    SM_SYMBOL_NAME TEXT
                    );'''.format(tableName=TABLE_NAME)

INSERT_DATA_QUERY = '''INSERT INTO {tableName} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'''.format(
    tableName=TABLE_NAME)

CLEAR_TABLE_QUERY = 'DELETE FROM {tableName};'.format(tableName=TABLE_NAME)


def download_csv_from_url():
    response = requests.get(url)
    if response.status_code == 200:
        with open(_filename, 'wb') as file:
            file.write(response.content)
        print(f"CSV file downloaded successfully as '{_filename}'")
    else:
        print("Failed to download CSV file")


def read_csv(file_path):
    return pd.read_csv(file_path, low_memory=False)  # Added low_memory=False here


def _create_table(cursor, query):
    cursor.execute(query)


def _insert_data(cursor, query, data):
    cursor.executemany(query, data)


def _clear_table(cursor, query):
    cursor.execute(query)


def _store_csv_to_sqlite(filenames: list, db_filename: str, clear_table_query: str, create_table_query: str,
                         insert_data_query: str):
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()

    try:
        _clear_table(cursor, clear_table_query)
    except Exception as e:
        logger.error(f"Error in clearing dhan scrip table due to: {e}")

    _create_table(cursor, create_table_query)

    for filename in filenames:
        df = read_csv(filename)

        data = df.values.tolist()
        _insert_data(cursor, insert_data_query, data)
        print(f"Inserted data from {filename} into SQLite database.")

    conn.commit()
    conn.close()


def store_csv_to_sqlite():
    _store_csv_to_sqlite([_filename], _db_filename, CLEAR_TABLE_QUERY, CREATE_TABLE_QUERY, INSERT_DATA_QUERY)


def download_store_delete_csv():
    download_csv_from_url()
    store_csv_to_sqlite()
    os.remove(_filename)


def getSecurityIdFromTradingSymbol(symbol: str, exchange: str, segment: str):
    conn = sqlite3.connect(_db_filename)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT SEM_SMST_SECURITY_ID 
            FROM dhan_scrip_data 
            WHERE SEM_TRADING_SYMBOL LIKE ? 
            AND SEM_EXM_EXCH_ID LIKE ? 
            AND SEM_INSTRUMENT_NAME = ?
        """, [symbol, exchange, segment])
    except Exception as e:
        logger.error(f"Error in fetching data from db due to: {e}")
        conn.close()
        return None

    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


def get_token_and_exchange_from_symbol(symbol):
    conn = sqlite3.connect(_db_filename)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT SEM_SMST_SECURITY_ID, SEM_EXM_EXCH_ID FROM dhan_scrip_data WHERE SEM_TRADING_SYMBOL = ?",
                       (symbol,))
    except:
        download_csv_from_url()
        store_csv_to_sqlite()
        cursor.execute("SELECT SEM_SMST_SECURITY_ID, SEM_EXM_EXCH_ID FROM dhan_scrip_data WHERE SEM_TRADING_SYMBOL = ?",
                       (symbol,))
    row = cursor.fetchone()
    conn.close()
    return row if row else None


if __name__ == "__main__":
    # download_store_delete_csv()
    print(getSecurityIdFromTradingSymbol("YESBANK", "NSE", "EQUITY"))
    # Test the functions
    # print(get_token_id_from_symbol("TAPARIA", "BSE"))
    # print(get_token_id_from_symbol("SBIN", "NSE"))
    # print(get_token_id_from_symbol("NIFTY31OCT2424700CE", "NFO"))
    # print(get_token_and_exchange_from_symbol("SBIN"))