import re
from pathlib import Path
from argparse import ArgumentParser

import numpy as np
import pandas as pd
import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output


ap = ArgumentParser()
ap.add_argument('--log_dir',
                default=str(Path("C:/Users/Amos/Documents/My Games/Sid Meier's Civilization VI/Logs")))
args = ap.parse_args()


def get_completed_techs(src,
                        player_num):
    df = pd.read_csv(src)
    df = df[df[' Player'] == player_num]
    completed_tech = [x.strip() for x in df[df[' Turns'] <= 1][' Tech'].unique().tolist()]
    return completed_tech


def get_current_tech(src,
                     player_num):
    df = pd.read_csv(src)
    df = df[df[' Player'] == player_num]
    temp = df[df[' Boost'] == ' RESEARCHING']
    tech = temp.iloc[-1][' Tech']
    turns_remaining = temp.iloc[-1][' Turns']
    total_turns = temp[temp[' Tech'] == tech][' Turns'].max()
    return tech, int(turns_remaining), int(total_turns)


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
    d['player_num'] = int(m.group().split(' ')[-1])

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


def format_leader_options(row):
    return f'{row["leader"]} ({row["civilization"]})'


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


def create_leader_radio(leader_df,
                        leader_dir='assets/leaders'):
    d = {'KUBLAI_KHAN_CHINA': 'kublai_khan',
         'T_ROOSEVELT_ROUGHRIDER': 't_roosevelt'}
    leader_dir = Path(__file__).parent.joinpath(leader_dir)
    data = []
    for leader in leader_dir.iterdir():
        datum = {'name': leader.stem,
                 'fp': f'/assets/leaders/{leader.name}'}
        data.append(datum)
    leader_icon_df = pd.DataFrame(data)

    leader_df['fp'] = ''
    for idx, row in leader_df.iterrows():
        eph = row['leader'].replace(' ', '_')
        if eph in d.keys():
            eph = d[eph]
        temp = leader_icon_df[leader_icon_df['name'].str.contains(eph, flags=re.IGNORECASE)]
        temp = temp.reset_index(drop=True)
        leader_df.at[idx, 'fp'] = temp.at[0, 'fp']

    leaders_radio = dcc.RadioItems(
        [
            {
                'label': html.Div(
                    [
                        html.Img(src=row['fp'])
                    ]
                ),
                'value': row['leader']
            }
        for idx, row in leader_df.iterrows()]
    , id='leader-radio', value=leader_df['leader'].values[0])
    return leaders_radio


TECHS = np.array(
    [
        [
            None,
            None,
            None,
            'Pottery',
            'Animal Husbandry',
            None,
            'Mining',
            None
        ],
        [
            'Sailing',
            'Astrology',
            'Irrigation',
            'Writing',
            'Archery',
            None,
            None,
            None
        ],
        [
            None,
            None,
            None,
            None,
            None,
            'Masonry',
            'Bronze Working',
            'The Wheel'
        ],
        [
            None,
            'Celestial Navigation',
            None,
            'Currency',
            'Horseback Riding',
            None,
            'Iron Working',
            None
        ],
        [
            'Shipbuilding',
            None,
            'Mathematics',
            None,
            None,
            'Construction',
            None,
            'Engineering'
        ],
        [
            'Buttress',
            'Military Tactics',
            None,
            'Apprenticeship',
            None,
            None,
            None,
            'Machinery'
        ],
        [
            None,
            None,
            'Education',
            None,
            'Stirrups',
            'Military Engineering',
            'Castles',
            None
        ],
        [
            'Cartography',
            'Mass Production',
            None,
            'Banking',
            'Gunpowder',
            None,
            None,
            'Printing'
        ],
        [
            'Square Rigging',
            None,
            'Astronomy',
            None,
            'Metal Casting',
            None,
            'Siege Tactics',
            None
        ],
        [
            None,
            'Industrialization',
            'Scientific Theory',
            None,
            'Ballistics',
            None,
            'Military Science',
            None
        ],
        [
            'Steam Power',
            None,
            'Sanitation',
            'Economics',
            None,
            'Rifling',
            None,
            None
        ],
        [
            None,
            'Flight',
            None,
            'Replaceable Parts',
            'Steel',
            None,
            'Refining',
            None
        ],
        [
            'Electricity',
            'Radio',
            'Chemistry',
            None,
            None,
            'Combustion',
            None,
            None
        ],
        [
            None,
            'Advanced Flight',
            'Rocketry',
            'Advanced Ballistics',
            'Combined Arms',
            'Plastics',
            None,
            None
        ],
        [
            'Computers',
            None,
            None,
            None,
            'Nuclear Fission',
            'Synthetic Materials',
            None,
            None
        ],
        [
            'Telecommunications',
            None,
            'Satellites',
            'Guidance Systems',
            'Lasers',
            'Composites',
            'Stealth Technology',
            None
        ],
        [
            None,
            'Robotics',
            None,
            None,
            'Nuclear Fusion',
            'Nanotechnology',
            None,
            None
        ]
    ]
)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

plot_layout = go.Layout(title={'text': '',
                               'font': {'size': 22,
                                        'family': 'Raleway',
                                        'color': 'white'},
                               'x': 0.5,
                               'y': 0.9,
                               'xanchor': 'center',
                               'yanchor': 'top'},
                        xaxis={'title': '',
                               'tickfont': {'size': 18,
                                            'family': 'Roboto',
                                            'color': 'white'},
                               'titlefont': {'size': 18,
                                             'family': 'Raleway',
                                             'color': 'white'}},
                        yaxis={'title': '',
                               'tickfont': {'size': 14,
                                            'family': 'Roboto',
                                            'color': 'white'},
                               'titlefont': {'size': 18,
                                             'family': 'Raleway',
                                             'color': 'white'},
                               'tickmode': 'linear',
                               'tick0': 0,
                               'dtick': 1},
                        width=250,
                        height=750,
                        paper_bgcolor='#5e5e5e',
                        plot_bgcolor='rgba(61, 61, 61, 0)'
                        )

leader_src = str(Path(args.log_dir).joinpath('GameCore.log'))
leaders_df = pd.DataFrame(get_leaders(leader_src))
leaders_df = leaders_df[leaders_df['civilization_type'] == 'FULL_CIV']

for civilization in leaders_df['leader']:
    eph = leaders_df[leaders_df['leader'] == civilization.upper()]['player_num'].values[0]
leaders_radio = create_leader_radio(leaders_df)

src = str(Path(args.log_dir).joinpath('AI_Research.csv'))
df = pd.read_csv(src)
num_turns = int(df[' Turns'].max())


turns_dropdown = dcc.Dropdown(options=[x for x in range(1, num_turns + 1)],
                              value=num_turns)
interval = dcc.Interval(id='interval',
                        interval=1000 * 1,
                        n_intervals=0)

t = []
for x in range(TECHS.shape[1]):
    for y in range(TECHS.shape[0]):
        tech = TECHS[y, x]
        if tech:
            name = f'TECH_{tech.replace(" ", "_").upper()}'
            element = html.Div(children=html.H2(children=tech, id=name), className='tech')
        else:
            element = html.Div(className='blank-tech')
        t.append(element)


data = [go.Bar(x=['Tech'],
               y=[1])]
dummy = go.Figure(data=data,
                  layout=plot_layout)
button = html.Button('Back', id='back-button', n_clicks=0)

app.layout = html.Div(children=[
    html.Div(children=[
        dcc.Graph(figure=dummy, id='current-research')], className='sidebar'),
    html.Div(children=[
        html.Div([
            leaders_radio,
            interval
            ]),
        html.Div(children=t, className='tech-tree', id='tech-tree')
    ], className='tech-tree-container', id='tech-tree-container')
], className='four-by-four')


@app.callback(Output(component_id='tech-tree', component_property='children'),
              Output(component_id='current-research', component_property='figure'),
              Input(component_id='leader-radio', component_property='value'),
              Input(component_id='interval', component_property='n_intervals'))
def update_layout(leader, n):
    player_num = leaders_df[leaders_df['leader'] == leader.upper()]['player_num'].values[0]
    t = []
    completed = ['_'.join(x.split('_')[1:]).lower() for x in get_completed_techs(src, player_num)]
    for x in range(TECHS.shape[1]):
        for y in range(TECHS.shape[0]):
            tech = TECHS[y, x]
            if tech and tech.replace(' ', '_').lower() in completed:
                e = html.Div(children=html.H2(children=tech, id=name), className='tech-completed')
            elif tech and tech.replace(' ', '_').lower() not in completed:
                e = html.Div(children=html.H2(children=tech, id=name), className='tech')
            else:
                e = html.Div(className='tech-blank')
            t.append(e)

    leaders_radio = create_leader_radio(leaders_df)
    leaders_radio.value = leader

    layout = html.Div([
                    leaders_radio,
                    interval
                    ]),
                html.Div(children=t, className='tech-tree')

    try:
        tech, turns, total_turns = get_current_tech(src,
                                                    player_num)
        tech = ' '.join(tech.split('_')[1:]).title()
    except IndexError:
        tech = 'tech'
        turns = 1
        total_turns = 10

    traces = [go.Bar(x=[tech],
                     y=[total_turns - turns + 1],
                     marker={'color': '#f9ab00'})]
    fig = go.Figure(data=traces,
                    layout=plot_layout)
    fig.update_layout(yaxis={'range': [0, total_turns]})

    return layout, fig


if __name__ == '__main__':
    # update_layout('Arabia', 0)
    app.run_server(debug=True)
