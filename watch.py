import re
import sys
import time
from pathlib import Path 
from argparse import ArgumentParser

import pandas as pd
import sqlalchemy as db 
from tqdm import tqdm 

from importer import create_table


def open_core_log(src):
    with open(src, 'r') as f:
        lines = f.readlines()
    series = pd.Series(lines)
    return series


def find_start_line(src):
    series = open_core_log(src)
    temp = series[series.str.contains(r'Initializing player from config:', flags=re.IGNORECASE)]
    return temp.index.values[-1]


def parse_leader(line):
    lines = line.split(' - ')
    d = {}

    m = re.match(r'Player [0-9]*', lines[0])
    d['player_id'] = int(m.group().split(' ')[-1])

    m = re.match(r'CIVILIZATION_[A-Za-z_]*', lines[1])
    d['civilization'] = m.group().split(' ')[0].split('CIVILIZATION_')[-1]

    try:
        m = re.match(r'LEADER_[A-Z_]*', lines[2])
        d['leader'] = ' '.join(m.group().split('_')[1:])
    except AttributeError:
        d['leader'] = 'BARBARIAN'

    m = re.match(r'CIVILIZATION_LEVEL_[A-Z_]*', lines[4])
    d['civilization_type'] = m.group().split('CIVILIZATION_LEVEL_')[-1]

    d['player_type'] = lines[-1]
    return d


def get_leaders(src):
    start_line = find_start_line(src)
    series = open_core_log(src)
    leaders = []
    for line_num in range(start_line + 1, series.shape[0]):
        line = series.values[line_num]
        temp = re.split(r'\[[0-9].*[0-9].\]', line)
        if re.match(r'Player [0-9]*:', temp[-1].strip()):
            d = parse_leader(temp[-1].strip())
            leaders.append(d)
    return leaders


def get_completed_techs(df,
                        player_num):
    df = df[df['player_id'] == player_num]
    completed_tech = [x.strip() for x in df[df['turns'] <= 1]['tech'].unique().tolist()]
    return completed_tech


def get_game_id(src):
    series = open_core_log(src)
    line = series.iloc[0]
    match = re.search(r"\[(-?\d+(\.\d+)?)\]", line)
    game_id = match.group(1)
    return game_id


def are_dupes(df):
    dupes = df[df.duplicated(subset=['game_id', 'player_id', 'turn', 'tech'], keep=False)]
    if dupes.any():
        return True
    else:
        return False


def format_columns(df):
    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.lower()
    df.columns = df.columns.map(lambda x: '_'.join(x.split()))
    df = df.rename({
        'game turn': 'turn'
    }, axis=1)
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    return df 


def to_sql(df, table, game_id, conn):
    # data_types = {
    #     'game_id': object,
    #     'player_id': int,
    #     'civilization': object,
    #     'leader': object,
    #     'turn': int,
    #     'action': object,
    #     'tech': object,
    #     'score': float,
    #     'boost': object,
    #     'turns': object
    # }

    query = f"SELECT * FROM {table} WHERE game_id = '{game_id}';"
    existing = pd.read_sql_query(query, conn)

    # for k, v in df.dtypes.items():
    #     if k in existing.columns:
    #         if v != existing[k].dtype:
    #             existing[k] = existing[k].astype(df[k].dtype)
    
    # df['turn'] = pd.to_numeric(df['turn'], errors='raise')
    # existing['turn'] = pd.to_numeric(existing['turn'], errors='raise')

    dupes = df.merge(existing,
                     how='inner',
                     on=df.columns.tolist(),
                    #  left_on=df.columns.tolist(),
                    #  right_on=existing.columns.tolist()
                     )
    new = df.drop([x for x in dupes.index if x in df.index], axis=0)
    new.to_sql(table, conn, index=False, if_exists='append')
    conn.commit()

    # for idx, row in tqdm(df.iterrows(), total=df.shape[0]):
    #     temp = row.to_frame().transpose()
    #     try:
    #         temp.to_sql(table, conn, index=False, if_exists='append')
    #         conn.commit()
    #     except db.exc.IntegrityError:
    #         continue


def get_game(src, conn):
    game_id = get_game_id(src)
    data = {'game_id': game_id,
            'start_time': pd.to_datetime('now')}
    df = pd.DataFrame([data])
    try:
        df.to_sql('Games', conn, index=False, if_exists='append')
        conn.commit()
    except db.exc.IntegrityError:
        pass

    while True:
        try:
            leaders_df = pd.DataFrame(get_leaders(src))
            leaders_df = leaders_df[leaders_df['civilization_type'] == 'FULL_CIV']
            leaders_df['game_id'] = game_id
            break
        except IndexError:
            continue

    to_sql(leaders_df, 'Players', game_id, conn)

    return game_id, leaders_df


def get_research(src, game_id, conn):
    df = pd.read_csv(src)
    df['game_id'] = game_id
    df = df.rename({
        ' Player': 'player_id',
        'Game Turn': 'turn',
        ' Action': 'action',
        ' Tech': 'tech',
        ' Score': 'score',
        ' Boost': 'boost',
        ' Turns': 'turns'
    }, axis=1)
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    to_sql(df, 'Research', game_id, conn)
    conn.execute(db.text('CALL civDW.completed_techs;'))
    conn.commit()
    

def get_yields(src, leaders_df, game_id, conn):
    df = pd.read_csv(src)   
    df[' Player'] = df[' Player'].map(lambda x: x.split('_')[-1])
    df = df.merge(leaders_df[['player_id', 'civilization']],
              how='inner',
              left_on=' Player',
              right_on='civilization')
    df = df.drop([' Player', 'civilization'], axis=1)
    df = df.rename({x: x.strip() for x in df.columns}, axis=1)
    df = df.rename({
        'Game Turn': 'turn',
        'TILES: Owned': 'tiles_owned',
        'Improved': 'tiles_improved',
        'BALANCE: Gold': 'gold_balance',
        'Faith': 'faith_balance',
        'YIELDS: Science': 'science_per_turn',
        'Culture': 'culture_per_turn',
        'Faith.1': 'faith_per_turn',
        'Gold': 'gold_per_turn',
        'Production': 'production_per_turn',
        'Food': 'food_per_turn'
    }, axis=1)
    df = format_columns(df)
    df['game_id'] = game_id
    to_sql(df, 'Yields', game_id, conn)


def get_city_builds(src, ai_build, leaders_df, game_id, conn):
    df = pd.read_csv(src)
    df = format_columns(df)
    df = df.rename({
        'game_turn': 'turn'
    }, axis=1)

    ai_df = pd.read_csv(ai_build, header=None, dtype=str, skiprows=1)
    ai_df = ai_df.drop(columns=[12, 13], axis=1)  # Drop the first column
    ai_df.columns = ['Game Turn', 'Player', 'City', 'Food Adv.', 'Prod. Adv.', 'Construct', 'Food', 'Production', 'Gold', 'Science', 'Culture', 'Faith']
    ai_df['Player'] = ai_df['Player'].map(lambda x: int(x.strip()))
    ai_df = format_columns(ai_df)
    ai_df = ai_df.rename({'game_turn': 'turn',
                          'player': 'player_id',
                          'food_adv.': 'food_adv',
                          'prod._adv.': 'prod_adv'}, axis=1)
    ai_df['game_id'] = game_id
    leaders = ai_df[['player_id', 'city']].drop_duplicates()
    df = df.merge(leaders,
              how='left',
              on='city')
    
    df = df.merge(leaders_df[['player_id']],
                  how='inner',
                  on='player_id')
    df['game_id'] = game_id
    df = df.drop_duplicates(subset=df.columns.tolist(), keep='first')
    to_sql(df, 'CityBuild', game_id, conn)
    ai_df['turn'] = pd.to_numeric(ai_df['turn'], errors='coerce')
    to_sql(ai_df, 'AICityBuild', game_id, conn)


def get_espionage(src, game_id, conn):
    df = pd.read_csv(src, header=None, skiprows=1)
    columns = ['turn', 
           'player_id', 
           'city', 
           'UNITOPERATION_SPY_LISTENING_POST'.lower(),
           'UNITOPERATION_SPY_GAIN_SOURCES'.lower(),
           'UNITOPERATION_SPY_STEAL_TECH_BOOST'.lower(),
           'UNITOPERATION_SPY_GREAT_WORK_HEIST'.lower(),
           'UNITOPERATION_SPY_SABOTAGE_PRODUCTION'.lower(),
           'UNITOPERATION_SPY_SIPHON_FUNDS'.lower(),
           'UNITOPERATION_SPY_REC'.lower(),
           'a',
           'b',
           'c',
           'd'
           ]
    df.columns = columns
    df['game_id'] = game_id 
    to_sql(df, 'Espionage', game_id, conn)


def get_policies(src, game_id, conn):
    df = pd.read_csv(src)
    df = format_columns(df)
    df = df.rename({'game_turn': 'turn',
                    'player': 'player_id'}, axis=1)
    df['game_id'] = game_id
    to_sql(df, 'Policies', game_id, conn)


def get_beliefs(src, game_id, conn):
    df = pd.read_csv(src)
    df = format_columns(df)
    df = df.rename({'game_turn': 'turn',
                    'player': 'player_id'}, axis=1)
    df['game_id'] = game_id
    to_sql(df, 'Beliefs', game_id, conn)


def get_score(src, game_id, conn):
    df = pd.read_csv(src)
    df = format_columns(df)
    df['game_id'] = game_id
    df = df.rename({'game_turn': 'turn',
                    'player': 'player_id'}, axis=1)
    to_sql(df, 'Scores', game_id, conn)


def create_tables(conn):
    if not db.inspect(conn).has_table('Research'):
        create_table('./sql/tables/civLOG/Research.sql', conn)
    
    if not db.inspect(conn).has_table('Games'):
        create_table('./sql/tables/civLOG/Games.sql', conn)

    if not db.inspect(conn).has_table('CityBuild'):
        create_table('./sql/tables/civLOG/CityBuild.sql', conn)

    if not db.inspect(conn).has_table('AICityBuild'):
        create_table('./sql/tables/civLOG/AICityBuild.sql', conn)

    if not db.inspect(conn).has_table('Espionage'):
        create_table('./sql/tables/civLOG/Espionage.sql', conn)

    if not db.inspect(conn).has_table('Players'):
        create_table('./sql/tables/civLOG/Players.sql', conn)

    if not db.inspect(conn).has_table('Yields'):
        create_table('./sql/tables/civLOG/Yields.sql', conn)

    if not db.inspect(conn).has_table('Policies'):
        create_table('./sql/tables/civLOG/Policies.sql', conn)


def main(args):
    username = 'amos'
    password = 'M0$hicat'
    host = '192.168.0.131'
    port = '3306'
    database = 'civLOG'
    connection_string = connection_string = f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}'
    engine = db.create_engine(connection_string)
    with engine.connect() as conn:
        create_tables(conn)

        src = Path(args.log_dir).joinpath('GameCore.log')
        while not src.exists():
            time.sleep(1)

        game_id, leaders_df = get_game(src, conn)      

        print('Connected. Starting to watch for new games...')
        while True:
            src = Path(args.log_dir).joinpath('AI_Research.csv')
            if src.exists():
                get_research(src, game_id, conn)

            src = Path(args.log_dir).joinpath('Player_Stats.csv')
            if src.exists():
                get_yields(src, leaders_df, game_id, conn)

            ai_build = Path('/home/amos/.local/share/aspyr-media/Sid Meier\'s Civilization VI/Logs/AI_CityBuild.csv')
            src = Path('/home/amos/.local/share/aspyr-media/Sid Meier\'s Civilization VI/Logs/City_BuildQueue.csv')
            if src.exists() and ai_build.exists():
                get_city_builds(src, ai_build, leaders_df, game_id, conn)

            src = Path(args.log_dir).joinpath('AI_Espionage.csv')
            if src.exists():
                get_espionage(src, game_id, conn)

            src = Path(args.log_dir).joinpath('AI_GovtPolicies.csv')
            if src.exists():
                get_policies(src, game_id, conn)

            src = Path(args.log_dir).joinpath('Game_PlayerScores.csv')
            if src.exists():
                get_score(src, game_id, conn)


            src = Path(args.log_dir).joinpath('Game_PlayerScores.csv')
            if src.exists():
                get_score(src, game_id, conn)


if __name__ == '__main__':
    ap = ArgumentParser()
    ap.add_argument('--log_dir', default='/home/amos/.local/share/aspyr-media/Sid Meier\'s Civilization VI/Logs/')
    args = ap.parse_args()
    main(args)
