import sqlite3
import os
import pandas as pd
from logzero import logger

script_dir = os.path.dirname(os.path.abspath(__file__))
_db_filename = os.path.join(script_dir, '../scrip_master.db')
csv_filename = os.path.join(script_dir, "dhan_scrip_master.csv")
_filename = csv_filename

# Dynamically generate CREATE TABLE query based on the CSV headers
def generate_create_table_query(df):
    # Map the column names and choose appropriate SQLite data types
    columns = df.columns
    create_table_query = "CREATE TABLE IF NOT EXISTS dhan_scrip_data (\n"
    
    # Iterate through columns and assign types
    for col in columns:
        if "ID" in col or "CODE" in col or "PRICE" in col or "LOT_UNITS" in col:
            create_table_query += f"    {col} REAL,\n"
        elif "DATE" in col or "EXPIRY" in col:
            create_table_query += f"    {col} TEXT,\n"
        else:
            create_table_query += f"    {col} TEXT,\n"
    
    create_table_query = create_table_query.rstrip(",\n") + "\n);"
    return create_table_query

def read_csv(file_path):
    return pd.read_csv(file_path)

def _create_table(cursor, create_table_query):
    cursor.execute(create_table_query)

def _insert_data(cursor, table_name, data):
    placeholders = ', '.join(['?'] * len(data.columns))
    query = f"INSERT INTO {table_name} VALUES ({placeholders})"
    cursor.executemany(query, data.values.tolist())

def _clear_table(cursor, table_name):
    cursor.execute(f"DELETE FROM {table_name}")

def store_csv_to_sqlite():
    conn = sqlite3.connect(_db_filename)
    cursor = conn.cursor()
    
    df = read_csv(_filename)

    # Generate the CREATE TABLE query dynamically
    create_table_query = generate_create_table_query(df)

    # try:
    #     _clear_table(cursor, "dhan_scrip_data")
    # except Exception as e:
    #     logger.error(f"Error in clearing dhan scrip table due to: {e}")
    
    # Create the table
    _create_table(cursor, create_table_query)

    # Insert data into the table
    _insert_data(cursor, "dhan_scrip_data", df)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    # Store CSV to SQLite
    store_csv_to_sqlite()

def getSecurityIdFromTradingSymbol(symbol: str):
    conn = sqlite3.connect(_db_filename)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT SEM_SMST_SECURITY_ID FROM dhan_scrip_data WHERE SEM_TRADING_SYMBOL like ?",
                       [symbol])
    except Exception as e:
        logger.error("Error in fetching data from db due to: {e}".format(e=e))

    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]
    else:
        return None

def getSymbolFrom():
    return "SYM"
