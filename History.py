import sqlite3

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from sklearn.preprocessing import MinMaxScaler


def traces_from_df(df,
                   normalize=False,
                   line_type=None):
    colors = {'science': 'blue',
              'culture': 'purple',
              'production': 'brown'}
    if normalize:
        scaler = MinMaxScaler()
    else:
        scaler = None
    traces = []
    for column in df.columns:
        if scaler is not None:
            df[column] = scaler.fit_transform(df[column].values.reshape(-1, 1))

        trace = go.Scatter(x=df.index,
                           y=df[column],
                           name=column,
                           line={'color': colors[column.lower().split('_')[-1]],
                                 'dash': line_type})

        traces.append(trace)
    return traces


class History(object):
    def __init__(self,
                 db,
                 game_id=None,
                 player_id=None):
        self.conn = sqlite3.connect(db)
        self.game_id = game_id
        self.player_id = player_id

        if not self.game_id:
            df = pd.read_sql_query('SELECT * FROM Games', self.conn)
            self.game_id = df['GameId'].values[-1]

        if not self.player_id:
            self.player_id = self.player_id_from_game_id(self.game_id)

    def player_id_from_game_id(self,
                               game_id):
        """
        There is no direct way of tying the player_id to the game_id in the sql database. However, the length of the list of
        human players is, naturally, equal to the number of games, so we can find the player_id by finding the index
        position of the game and using that to access the list of player_ids.
        :param game_id: id used for retrieving information pertaining to that game
        :type game_id: int
        :return:
        """
        games = pd.read_sql_query('SELECT * FROM Games', self.conn)
        game = games[games['GameId'] == game_id]
        idx = game.index.values[0]
        game_players = pd.read_sql_query('SELECT * FROM GamePlayers', self.conn)
        me = game_players[game_players['PlayerId'] == 0]
        player = me.iloc[idx]
        player_id = player['PlayerObjectId']
        return player_id

    def get_dataset(self,
                    player_id,
                    dataset):
        datasets = pd.read_sql_query('SELECT * FROM DataSets', self.conn)
        dataset_values = pd.read_sql_query('SELECT * FROM DataSetValues', self.conn)

        df = datasets[datasets['ObjectId'] == player_id]
        civics = df[df['DataSet'] == dataset]
        dataset_id = civics['DataSetId'].values[0]
        df = dataset_values[dataset_values['DataSetId'] == dataset_id]
        df = df[['X', 'Y']]
        df.set_index('X', inplace=True)
        return df

    def data_from_city_id(self,
                          idx,
                          field):
        """

        :param idx:
        :param field:
        :return:
        """
        df = pd.read_sql_query('SELECT * FROM DataSets', self.conn)
        dataset = df[df['ObjectId'] == idx]
        if dataset.empty:
            return None
        dataset_id = dataset[dataset['DataSet'] == field]['DataSetId'].values[0]
        data_df = pd.read_sql_query('SELECT * FROM DataSetValues', self.conn)
        data = data_df[data_df['DataSetId'] == dataset_id]
        data = data[['X', 'Y']]
        data.set_index('X', inplace=True)
        return data

    def cities_over_time(self,
                         player_id):
        df = pd.read_sql_query('SELECT * FROM GameObjects', self.conn)
        player_objects = df[df['PlayerObjectId'] == player_id]['ObjectId'].values
        cities = []
        for i in player_objects:
            city = self.data_from_city_id(i,
                                          'Science')        # 'Science' is just a dummy parameter
            cities.append(city)
        df = pd.concat(cities, axis=1)
        df['counts'] = df.count(axis=1)
        return df['counts']

    def data_from_empire(self,
                         player_id,
                         field):
        """
        The data is organized by "dataset_id," which generally corresponds, in this case, to an object_id representing a
        city. The values for each city are then summed by turn. This is achieved in this function by concating pandas
        DataFrames representing an individual city, which are then summed along the columns.
        :param player_id: unique id tied to a specific player in a specific game
        :type player_id: int
        :param field: the yield to be measured (e.g., 'production')
        :type field: str
        :return: a pandas DataFrame containing the aggregated yields for the specified fields
        """
        df = pd.read_sql_query('SELECT * FROM GameObjects', self.conn)
        player_objects = df[df['PlayerObjectId'] == player_id]['ObjectId'].values
        data = []
        for i in player_objects:
            datum = self.data_from_city_id(i,
                                           field)
            data.append(datum)

        merged = pd.concat(data,
                           axis=1,
                           ignore_index=False,
                           sort=True)
        merged.fillna(0, inplace=True)
        merged[field] = merged.sum(axis=1)
        merged = merged[[field]]
        return merged

    def create_game_plots(self,
                          game_data,
                          normalize=True,
                          num_cols=2,
                          cities=False):
        if num_cols == 1:
            traces = []
            lines = [None, 'dash']
            for df in game_data:
                t = traces_from_df(df,
                                   normalize=normalize,
                                   line_type=lines.pop(np.random.randint(0, len(lines))))
                traces.extend(t)
            fig = go.Figure(data=traces)
        else:
            q, r = divmod(len(game_data), num_cols)
            if r != 0:
                num_rows = q + 1
            else:
                num_rows = q
            fig = make_subplots(rows=num_rows,
                                cols=num_cols,
                                specs=[[{"secondary_y": True}] * len(game_data)])
            for num, df in enumerate(game_data):
                traces = traces_from_df(df,
                                        normalize=normalize)

                q, _ = divmod(num, num_cols)
                row = q + 1
                col = (num % num_cols) + 1

                for trace in traces:
                    fig.add_trace(trace,
                                  row=row,
                                  col=col,
                                  secondary_y=False)

                if cities:
                    player_id = self.player_id_from_game_id(df.name)
                    city = self.cities_over_time(player_id)
                    trace = go.Bar(x=city.index,
                                   y=city.values,
                                   opacity=0.5)
                    fig.add_trace(trace,
                                  row=row,
                                  col=col,
                                  secondary_y=True)
        return fig

    def by_type(self,
                player_id, t):
        df = pd.read_sql_query('SELECT * FROM ObjectDataPointValues', self.conn)
        df = df[df['ObjectId'] == player_id]
        df = df[df['DataPoint'] == t]
        df['ValueType'] = df['ValueType'].map(lambda x: " ".join(x.split('_')[1:]).lower().capitalize())
        df = df[['ValueType', 'ValueNumeric']]
        return df

    def plot_buildings_units(self,
                             player_id,
                             t):
        df = self.by_type(player_id, t)
        fig = px.bar(df, x='ValueType', y='ValueNumeric')
        fig.show()

    def plot_civics_acquired(self,
                             player_id):
        df = self.cities_over_time(player_id)
        traces = [go.Scatter(x=df.index,
                             y=df['Y'],
                             mode='lines')]
        fig = go.Figure(data=traces)
        fig.show()
