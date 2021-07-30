import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State

# Create main process and supress callback errors because some callbacks are for elements that will be dynamically added
app = dash.Dash(__name__,
                suppress_callback_exceptions=True)

mapbox_access_token = "pk.eyJ1IjoidmFsZW50aW5rb2xiIiwiYSI6ImNrcTJjN3c1MzA3dDYyd3Q0cXJkMHM2Z20ifQ.MQhwjbSVbpiufV9iL54rCw"

##
# MAP
##

# in here we draw the pins for the locations
scatter = go.Scattermapbox(
    lat=[],
    lon=[],
    mode='markers',
    fillcolor="grey",
    marker={'size': 20, 'symbol': []},
    text=[],
)

map = go.Figure(scatter)
map.update_layout(
    autosize=True,
    hovermode='closest',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        bearing=0,
        center=dict(
            lat=47.99352971943071,
            lon=7.84600324283098
        ),
        pitch=3,
        zoom=15
    ),
    margin={"r": 0, "t": 0, "l": 0, "b": 0}  # this maxes the map full screen
)
map.update_mapboxes(
    style="mapbox://styles/valentinkolb/ckr6bhndj0ocj18mxic5onwuk",

)

##
# DROPDOWN
##

sample_options = [{"label": f'Option{i}', "value": f'Option{i}'} for i in range(10)]

filter_dropdown = dcc.Dropdown(
    id="filter_dropdown",
    options=sample_options,
    value=[],
    multi=True,
    placeholder="Select a Filter ..."
)

##
# SLIDER
##

sample_years = {year: {'label': str(year)} for year in range(1900, 2022, 10)}

time_axis = dcc.Slider(
    id='time_axis',
    min=1900,
    max=2021,
    value=2000,
    marks=sample_years,
    included=False
)

##
# MAIN APP LAYOUT
##

app.layout = html.Div([

    html.H1("Freiburg", id="header"),

    dcc.Graph(id='freiburg_map', figure=map),

    html.Div(id="dropdown_area", children=[filter_dropdown]),

    html.Div(id="time_slider", children=[time_axis]),

    html.Div(id="content_area", children=[

        html.Div(id="content", children=[
            html.H1("Daten"),
            html.Div(id='filter_output'),
            html.Div(id='slider_output')
        ]),

    ])
])


##
# INTERACTIVITY
##

@app.callback(
    Output("filter_output", "children"),
    Input('filter_dropdown', 'value'))
def update_filter(value):
    return 'You have selected the following filters: "{}"'.format(value)


@app.callback(
    Output('slider_output', 'children'),
    Input('time_axis', 'value'))
def update_slider(value):
    return 'You have selected the year "{}"'.format(value)


@app.callback(
    Output('data_area', 'children'),
    Input('freiburg_map', 'clickData'),
    State('data_area', 'children')
)
def get_click_from_map(clickData, state):
    """
    the main callback: this reacts to the clicks on the map

    Parameters
    ----------
    clickData :
        the location of the map
    state :
        the current state (the thing that is currently desplayed in the data area)

    Returns
    -------
    state:
        the new state
    """
    if clickData:
        location = clickData['points'][0]['text']
        print(f'{clickData=}')
    else:
        return state


##
# START PROGRAM
##

if __name__ == '__main__':
    app.run_server(debug=True)
