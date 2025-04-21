from pathlib import Path
from argparse import ArgumentParser 

import sqlite3 
import pandas as pd 
import sqlalchemy as db 


def create_table(fp,
                 conn):
    with open(Path(__file__).parent.joinpath(fp).absolute().resolve(), 'r') as f:
        text = f.read()
    text = text.replace('\t', ' ')
    text = text.replace('\n', '')
    statement = db.text(text)
    conn.execute(statement)
    conn.commit()


def num_games(sqlite_conn):
    sql_query = """SELECT COUNT(*) FROM games;"""
    cursor = sqlite_conn.cursor()
    cursor.execute(sql_query)
    num = cursor.fetchone()[0]
    return num


def main(args):
    username = 'amos'
    password = 'M0$hicat'
    host = '192.168.0.131'
    port = '3306'
    database = 'civ'
    connection_string = connection_string = f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}'
    engine = db.create_engine(connection_string)
    with engine.connect() as conn:
        d = Path(args.dir)
        files = [x for x in d.iterdir() if x.suffix == '.sqlite']
        for file in files:
            sqlite_conn = sqlite3.connect(str(file))
            num = int(file.stem.split('_')[-1])
            sql_query = """SELECT name FROM sqlite_master WHERE type='table';"""
            cursor = sqlite_conn.cursor()
            cursor.execute(sql_query)
            tables = [x[0] for x in cursor.fetchall()]

            for table in tables:
                name = f'{table}.sql'
                fp = Path('./sql/tables/').joinpath(name)
                if fp.exists():
                    if not db.inspect(engine).has_table(table):
                        create_table(fp, conn)
                    else:
                        ids = pd.read_sql_query(f'SELECT DISTINCT(hof_id) FROM {table}', conn)
                        if num not in ids['hof_id'].values:
                            df = pd.read_sql_query(f'SELECT * FROM {table};', sqlite_conn)
                            df['hof_id'] = num
                            df.to_sql(table, conn, index=False, if_exists='append')
                            conn.commit()


if __name__ == '__main__':
    ap = ArgumentParser()
    ap.add_argument('--dir', default='./hall_of_fame')
    args = ap.parse_args()
    main(args)
