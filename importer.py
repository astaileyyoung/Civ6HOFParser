import sqlite3 
import pandas as pd 
import sqlalchemy as db 


sqlite_conn = sqlite3.connect('HallofFame.sqlite')
df = pd.read_sql_query('SELECT * FROM Games', sqlite_conn)
sql_query = """SELECT name FROM sqlite_master  
  WHERE type='table';"""
cursor = sqlite_conn.cursor()
cursor.execute(sql_query)
tables = [x[0] for x in cursor.fetchall()]

username = 'amos'
password = 'M0$hicat'
host = '192.168.0.131'
port = '3306'
database = 'civ'
connection_string = connection_string = f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}'
conn = db.create_engine(connection_string)
for table in tables:
    df = pd.read_sql_query(f'SELECT * FROM {table};', sqlite_conn)
    df.to_sql(table, conn, index=False)


a = 1
