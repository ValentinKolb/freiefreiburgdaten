import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


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

##
# MAIN APP LAYOUT
##

app.layout = html.Div([

    # HEADER
    html.Div(
        html.Img(src=app.get_asset_url('logo_freiburg.png'),
                 style={'height': '80%', 'width': '80%', "display": "block", "margin": "0 auto"}),
        style={'width': '10%', 'display': 'inline-block'}
    ),
    html.Div(
        html.H1("Open-Data Freiburg"),
        style={'display': 'inline-block', "vertical-align": "middle"}
    ),

    html.Div([dcc.Graph(figure=px.choropleth_mapbox(data_frame=pd.DataFrame(),center={"lat": 48.00217366211979, "lon": 7.837318006483093},
                                          mapbox_style="open-street-map",
                                          zoom=8.5))]),

    # UNIVERSITY DATA
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
              ], style={'width': '33%', 'display': 'inline-block', 'vertical-align': 'top'}),

    # MAIN DATA AREA

])


##
# INTERACTIVITY
##

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
