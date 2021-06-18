import pandas as pd
from urllib.request import urlopen
import plotly.express as px
import json
import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

with open("/Users/valentinkolb/Git/freiefreiburgdaten/assets/.mapbox_accesstoken") as access_token:
    mapbox_access_token = access_token.read()


##
# HELPER TOOLS
##

def generate_table(dataframe: pd.DataFrame, max_rows: int = 26) -> html.Table:
    """
    generates table from dataframe

    Parameters
    ----------
    dataframe :
        the pandas dataframe
    max_rows :
        the max number of rows to be displayed

    Returns
    -------
    Table :
        a html table element
    """
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +
        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )


##
# DATA
##

df_number_students = pd.read_csv("/Users/valentinkolb/Git/freiefreiburgdaten/data/number_students.csv")
df_number_doctorate = pd.read_csv("/Users/valentinkolb/Git/freiefreiburgdaten/data/number_doctorate.csv")
df_number_graduate = pd.read_csv("/Users/valentinkolb/Git/freiefreiburgdaten/data/number_graduates.csv")

df = pd.DataFrame()

##
# MAP
##

scatter = go.Scattermapbox(
    lat=['47.9943809094517', '47.99352971943071'],
    lon=['7.844843887429616', '7.846003242830979'],
    mode='markers',
    fillcolor="grey",
    marker={'size': 20, 'symbol': ["library", "college"]},
    text=["Universitätsbibliothek", "Universität"],
)

fig = go.Figure(scatter)

fig.update_layout(
    autosize=True,
    hovermode='closest',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        bearing=0,
        center=dict(
            lat=47.99352971943071,
            lon=7.846003242830979
        ),
        pitch=3,
        zoom=15
    ),
)

##
# MAIN APP LAYOUT
##

app.layout = html.Div([

    # HEADER
    html.Div(
        [
            html.Img(src=app.get_asset_url('logo_freiburg.png'),
                     style={'display': 'table-cell', 'width': '80%', 'vertical-align': 'middle'}
                     ),
            html.H1("Open-Data Freiburg ... and more",
                    style={'display': 'table-cell', 'vertical-align': 'middle', 'width': '95%'}
                    )
        ], style={"display": "table", 'padding': '10px 60px'}
    ),

    dcc.Graph(id='freiburg_map', figure=fig),

    # DATA
    html.Div(id="data_area", children=[], style={'padding': '10px 60px'})

])

##
# UNIVERSITY DATA
##

university_layout = [
    html.H2("Daten über die Universität Freiburg"),

    html.Div(children=
             [dcc.Dropdown(id="no_students_year",
                           options=[
                               {"label": "Wintersemester 2016/17", "value": "WS 2016/17"},
                               {"label": "Wintersemester 2017/18", "value": "WS 2017/18"},
                               {"label": "Wintersemester 2018/19", "value": "WS 2018/19"},
                               {"label": "Wintersemester 2019/20", "value": "WS 2019/20"},
                               {"label": "Wintersemester 2020/21", "value": "WS 2020/21"}],
                           multi=False,
                           value="WS 2020/21",
                           style={'width': "100%"}
                           ),
              html.Div(id="no_students_table", children=[])
              ], style={'width': '33%', 'display': 'inline-block', 'vertical-align': 'top'}),

    html.Div(children=
             [dcc.Dropdown(id="no_doctorate_year",
                           options=[
                               {"label": "Wintersemester 2016/17", "value": "WS 2016/17"},
                               {"label": "Wintersemester 2017/18", "value": "WS 2017/18"},
                               {"label": "Wintersemester 2018/19", "value": "WS 2018/19"},
                               {"label": "Wintersemester 2019/20", "value": "WS 2019/20"},
                               {"label": "Wintersemester 2020/21", "value": "WS 2020/21"}],
                           multi=False,
                           value="WS 2020/21",
                           style={'width': "100%"}
                           ),
              html.Div(id="no_doctorate_table", children=[])
              ], style={'width': '33%', 'display': 'inline-block', 'vertical-align': 'top'}),

    html.Div(children=
             [dcc.Dropdown(id="no_graduate_year",
                           options=[
                               {"label": "Prüfungsjahr 2016", "value": "PJ 2016"},
                               {"label": "Prüfungsjahr 2017", "value": "PJ 2017"},
                               {"label": "Prüfungsjahr 2018", "value": "PJ 2018"},
                               {"label": "Prüfungsjahr 2019", "value": "PJ 2019"},
                               {"label": "Prüfungsjahr 2020", "value": "PJ 2020"}],
                           multi=False,
                           value="PJ 2020",
                           style={'width': "100%"}
                           ),
              html.Div(id="no_graduate_table", children=[])
              ], style={'width': '33%', 'display': 'inline-block', 'vertical-align': 'top'})
]


##
# INTERACTIVITY
##


@app.callback(
    Output('data_area', 'children'),
    Input('freiburg_map', 'clickData')
)
def get_click_from_map(clickData):
    if clickData:
        location = clickData['points'][0]['text']

        if location == 'Universitätsbibliothek':
            print("click on Universitätsbibliothek")
        elif location == 'Universität':
            print('click on Universität')
            return university_layout

    return []


@app.callback(
    [Output(component_id='no_students_table', component_property='children')],
    [Input(component_id='no_students_year', component_property='value')]
)
def update_table(selected):
    """
    this callback functions sets the selected year to the table displaying the student numbers
    """
    df_students = df_number_students.copy()
    df_students = df_students.filter(items=['Studierende', selected])

    return [generate_table(df_students)]


@app.callback(
    [Output(component_id='no_doctorate_table', component_property='children')],
    [Input(component_id='no_doctorate_year', component_property='value')]
)
def update_table(selected):
    """
    this callback functions sets the selected year to the table displaying the doctorate numbers
    """
    df_doctorate = df_number_doctorate.copy()
    df_doctorate = df_doctorate.filter(items=['Promovierende', selected])

    return [generate_table(df_doctorate)]


@app.callback(
    [Output(component_id='no_graduate_table', component_property='children')],
    [Input(component_id='no_graduate_year', component_property='value')]
)
def update_table(selected):
    """
    this callback functions sets the selected year to the table displaying the graduate numbers
    """
    df_graduate = df_number_graduate.copy()
    df_graduate = df_graduate.filter(items=['Absolvent*innen', selected])

    return [generate_table(df_graduate)]


##
# START PROGRAM
##

if __name__ == '__main__':
    app.run_server(debug=True)
