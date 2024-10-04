import json
import requests
import sqlite3
import os
import pandas as pd

from logzero import logger

# Setting up paths and database configuration
script_dir = os.path.dirname(os.path.abspath(__file__))
_db_filename = os.path.join(script_dir, '../oswal_scrip_master.db')
csv_filename = os.path.join(script_dir, "oswal_scrip.csv")


url = "https://openapi.motilaloswal.com/getscripmastercsv?name=NSE"
_filename = csv_filename

# SQL Queries
TABLE_NAME = "oswal_scrip_data"
CREATE_TABLE_QUERY = '''CREATE TABLE IF NOT EXISTS {tableName}(
                    ultoken TEXT,                  -- Token
                    scripshortname TEXT,           -- Symbol
                    scripfullname TEXT,            -- Name
                    expirydate TEXT,               -- Expiry Date
                    strikeprice TEXT,              -- Strike Price
                    marketlot TEXT,                -- Lot Size
                    instrumentname TEXT,           -- Instrument Type
                    exchange TEXT,                 -- Exchange/Segment
                    ticksize TEXT,                 -- Tick Size
                    exchangename TEXT,             -- Exchange Name
                    scripcode TEXT,                -- Scrip Code
                    issuspended TEXT,              -- Is Suspended
                    optiontype TEXT,               -- Option Type
                    markettype TEXT,               -- Market Type
                    lowerexchcircuitprice TEXT,    -- Lower Exchange Circuit Price
                    upperexchcircuitprice TEXT,    -- Upper Exchange Circuit Price
                    scripisinno TEXT,              -- Scrip ISIN Number
                    indicesidentifier TEXT,        -- Indices Identifier
                    isbanscrip TEXT,               -- Is Ban Scrip
                    facevalue TEXT,                -- Face Value
                    calevel TEXT,                  -- CA Level
                    maxqtyperorder TEXT            -- Max Qty per Order
                    );'''.format(tableName=TABLE_NAME)

INSERT_DATA_QUERY = '''INSERT INTO {tableName} (
                    ultoken, scripshortname, scripfullname, expirydate, strikeprice, marketlot, instrumentname,
                    exchange, ticksize, exchangename, scripcode, issuspended, optiontype, markettype,
                    lowerexchcircuitprice, upperexchcircuitprice, scripisinno, indicesidentifier, isbanscrip,
                    facevalue, calevel, maxqtyperorder
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'''.format(tableName=TABLE_NAME)


CLEAR_TABLE_QUERY = 'DELETE FROM {tableName};'.format(tableName=TABLE_NAME)


def download_csv_from_url():
    """
    Download the scrip data CSV from the Motilal Oswal API and store it locally.
    """
    response = requests.get(url)

    if response.status_code == 200:
        with open(_filename, 'wb') as file:
            file.write(response.content)
        print(f"CSV file downloaded successfully as '{_filename}'")
    else:
        print("Failed to download CSV file")


def read_csv(file_path):
    """
    Read the downloaded CSV file using pandas and return its contents as a list of dictionaries.
    """
    try:
        # Read the CSV file into a pandas DataFrame
        df = pd.read_csv(file_path)
        # Convert the DataFrame to a list of dictionaries
        objects = df.to_dict(orient='records')
        return objects
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        return []



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

    # try:
    #     # _clear_table(cursor, clear_table_query)
    # except Exception as e:
    #     logger.error(f"Error clearing scrip table: {e}")
    
    _create_table(cursor, create_table_query)

    for filename in filenames:
        df = read_csv(filename)

        data = []
        for obj in df:
            data.append((
            obj['ultoken'], obj['scripshortname'], obj['scripfullname'], obj['expirydate'], obj['strikeprice'], obj['marketlot'],
            obj['instrumentname'], obj['exchange'], obj['ticksize'], obj['exchangename'], obj['scripcode'], obj['issuspended'],
            obj['optiontype'], obj['markettype'], obj['lowerexchcircuitprice'], obj['upperexchcircuitprice'], obj['scripisinno'],
            obj['indicesidentifier'], obj['isbanscrip'], obj['facevalue'], obj['calevel'], obj['maxqtyperorder']
            ))

        _insert_data(cursor, insert_data_query, data)
        print(f"Inserted data from {filename} into SQLite database.")

        print(f"Inserted data from {filename} into SQLite database.")

    conn.commit()
    conn.close()


def store_csv_to_sqlite():
    _store_csv_to_sqlite([_filename], _db_filename, CLEAR_TABLE_QUERY, CREATE_TABLE_QUERY, INSERT_DATA_QUERY)


def download_store_delete_csv():
    download_csv_from_url()
    store_csv_to_sqlite()
    os.remove(_filename)



def get_token_id_from_symbol(symbol: str, exchange: str):
    """
    Get the token id from the symbol and exchange.
    """
    try:
        conn = sqlite3.connect(_db_filename)
        cursor = conn.cursor()
        
        # Query to get the ultoken from the database
        cursor.execute("SELECT ultoken FROM oswal_scrip_data WHERE scripshortname LIKE ? AND exchangename = ?", [symbol, exchange])
        
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else None  # Return the ultoken if found, else None

    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return None
    except Exception as e:
        logger.error(f"General error: {e}")
        return None


def get_token_and_exchange_from_symbol(symbol):
    """
    Get the token id and exchange from the symbol.
    """
    conn = sqlite3.connect(_db_filename)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT ultoken , exchangename FROM oswal_scrip_data WHERE scripshortname = ?", (symbol,))
    except:
        download_csv_from_url()
        store_csv_to_sqlite()
        cursor.execute("SELECT ultoken , exchangename FROM oswal_scrip_data WHERE scripshortname = ?", (symbol,))
    
    row = cursor.fetchone()
    conn.close()
    return row if row else None


if __name__ == "__main__":

    print(get_token_id_from_symbol("IDEA", "BSE"))
    print(get_token_id_from_symbol("MIDCPNIFTY", "NSEFO"))
    print(get_token_id_from_symbol("CUMMINSIND", "NSEFO"))

