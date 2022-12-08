import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

pd.set_option('display.max_columns', 13)
pd.set_option('display.width', 2000)

db = pd.read_csv('database/crimedata.csv', delimiter=',')
db['black'] = db['population'] * db['racepctblack'] / 100
db['white'] = db['population'] * db['racePctWhite'] / 100
db['asian'] = db['population'] * db['racePctAsian'] / 100
db['hispanic'] = db['population'] * db['racePctHisp'] / 100


db['from 12 to 21'] = db['population'] * db['agePct12t21'] / 100
db['from 12 to 29'] = db['population'] * db['agePct12t29'] / 100
db['from 16 to 24'] = db['population'] * db['agePct16t24'] / 100
db['under 65'] = db['population'] * db['agePct65up'] / 100


app = Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.H1("I hope, you will be fond of it)))"),
        html.Div([
            dcc.Dropdown(db['state'].unique(),
                        'NJ',
                        id='state'),
        ], style={'width': '49%', 'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(['murders', 'rapes', 'robberies', 'assaults'],
                        'murders',
                        id='crimes')
        ], style={'width': '49%', 'display': 'inline-block'})
    ]),
    html.Div([
        dcc.Graph(id='crimes_per_state')
    ], style={'height': '200%'}),
    html.Hr(),
    html.H1("Additional info about chosen community"),
    html.Div([
        dcc.Graph(id='races_per_community')
    ], style={'width': '32%', 'display': 'inline-block'}),
    html.Div([
        dcc.Graph(id='sadness')
    ], style={'width': '32%', 'display': 'inline-block'}),
    html.Div([
        dcc.Graph(id='ages_per_community')
    ], style={'width': '32%', 'display': 'inline-block'}),
    html.Hr(),
    html.Hr(),
    html.Div([
        dcc.Dropdown(['murders', 'rapes', 'robberies', 'assaults'],
                     'murders',
                     id='crimes_for_line')
    ], style={'width': '100%', 'display': 'inline-block'}),
    html.Div([
        dcc.Checklist(
            id="my-checklist",
            options=[
                {"label": "Speaks Only English", "value": "english"},
                {"label": "log type of graph", "value": "log"}
        ])
    ]),
    html.Div([
        dcc.Graph(id='crimes_per_races')
    ]),
])

@app.callback(
    Output('crimes_per_races', 'figure'),
    Input('my-checklist', 'value'),
    Input('crimes_for_line', 'value'))
def update_figure_pace_pie(my_selector, crimes_for_line):
    dynamic_of_crime_per_races = db[['white', 'black', 'asian', 'hispanic', 'PctSpeakEnglOnly', crimes_for_line]]
    dynamic_of_crime_per_races = dynamic_of_crime_per_races.dropna(how='any')
    if my_selector is not None and 'english' in my_selector:
        dynamic_of_crime_per_races['white'] = dynamic_of_crime_per_races['white'] * dynamic_of_crime_per_races['PctSpeakEnglOnly'] / 100
        dynamic_of_crime_per_races['asian'] = dynamic_of_crime_per_races['asian'] * dynamic_of_crime_per_races['PctSpeakEnglOnly'] / 100
        dynamic_of_crime_per_races['hispanic'] = dynamic_of_crime_per_races['hispanic'] * dynamic_of_crime_per_races['PctSpeakEnglOnly'] / 100
        dynamic_of_crime_per_races['black'] = dynamic_of_crime_per_races['black'] * dynamic_of_crime_per_races['PctSpeakEnglOnly'] / 100
    # dynamic_of_crime_per_races[[crimes_for_line]] = dynamic_of_crime_per_races[crimes_for_line].apply(lambda x: int(x // 5) * 5)
    dynamic_of_crime_per_races = dynamic_of_crime_per_races.groupby([crimes_for_line], as_index=False).mean()
    if my_selector is not None and 'log' in my_selector:
        dynamic_of_crime_per_races['white'] = np.log(dynamic_of_crime_per_races['white'])
        dynamic_of_crime_per_races['asian'] = np.log(dynamic_of_crime_per_races['asian'])
        dynamic_of_crime_per_races['hispanic'] = np.log(dynamic_of_crime_per_races['hispanic'])
        dynamic_of_crime_per_races['black'] = np.log(dynamic_of_crime_per_races['black'])
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=dynamic_of_crime_per_races['white'], x=dynamic_of_crime_per_races[crimes_for_line], name='white'))
    fig.add_trace(go.Scatter(y=dynamic_of_crime_per_races['asian'], x=dynamic_of_crime_per_races[crimes_for_line], name='asian'))
    fig.add_trace(go.Scatter(y=dynamic_of_crime_per_races['hispanic'], x=dynamic_of_crime_per_races[crimes_for_line], name='hispanic'))
    fig.add_trace(go.Scatter(y=list(dynamic_of_crime_per_races['black']), x=dynamic_of_crime_per_races[crimes_for_line], name='black'))
    fig.update_xaxes(title=crimes_for_line)
    if my_selector is not None and 'log' in my_selector:
        fig.update_yaxes(title='log(avg_amount_of_population)')
    else:
        fig.update_yaxes(title='avg_amount_of_population')
    return fig

@app.callback(
    Output('ages_per_community', 'figure'),
    Input('crimes_per_state', 'hoverData'),
    Input('state', 'value'),
    Input('crimes', 'value'))
def update_figure_pace_pie(hover, selected_state, selected_crime):
    if hover is not None:
        community = hover['points'][0]['y']
    else:
        community = "Newarkcity"
    crimes = db[db['communityName'] == community]
    crimes = crimes[['agePct12t21', 'agePct12t29', 'agePct16t24', 'agePct65up']]
    crimes = crimes.dropna(how='any')
    crimes = crimes.sum()
    fig = px.pie(values=list(crimes), names=list(crimes.index), color=list(crimes.index), title='Ages:')
    return fig


@app.callback(
    Output('sadness', 'figure'),
    Input('crimes_per_state', 'hoverData'),
    Input('state', 'value'),
    Input('crimes', 'value'))
def update_figure_pace_pie(hover, selected_state, selected_crime):
    if hover is not None:
        community = hover['points'][0]['y']
    else:
        community = "Newarkcity"
    crimes = db[db['communityName'] == community]
    crimes = crimes[['PctUnemployed', 'MalePctDivorce', 'FemalePctDiv']]
    crimes = crimes.dropna(how='any')
    crimes = crimes.sum()
    fig = px.bar(y=list(crimes), x=list(crimes.index), color=list(crimes.index), title='Status:')
    return fig

@app.callback(
    Output('races_per_community', 'figure'),
    Input('crimes_per_state', 'hoverData'),
    Input('state', 'value'),
    Input('crimes', 'value'))
def update_figure_pace_pie(hover, selected_state, selected_crime):
    if hover is not None:
        community = hover['points'][0]['y']
    else:
        community = "Newarkcity"
    races = db[db['communityName'] == community]
    races = races[['black', 'white', 'asian', 'hispanic']]
    races = races.dropna(how='any')
    races = races.sum()
    fig = px.pie(values=list(races), names=list(races.index), color=list(races.index), title='Races:')
    return fig


@app.callback(
    Output('crimes_per_state', 'figure'),
    Input('state', 'value'),
    Input('crimes', 'value'))
def update_figure_top_ten(selected_state, selected_crime):
    crime_states = db[db['state'] == selected_state].sort_values(by=selected_crime).tail(10)
    fig = px.bar(crime_states, y='communityName', x=selected_crime, title="Top 10 most crime communities per state ")
    return fig





if __name__ == '__main__':
    app.run_server(debug=True)
