import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State

# Create main process and supress callback errors because some callbacks are for elements that will be dynamically added
from data import load_data, filter_by_year, filter_by_category, pprint_dict
from styles import *

app = dash.Dash(__name__,
                suppress_callback_exceptions=True)

mapbox = {
    "style": "mapbox://styles/valentinkolb/cks7oj9h71aue18qne1ayk62t",
    "token": "pk.eyJ1IjoidmFsZW50aW5rb2xiIiwiYSI6ImNrczdtb3ZvNzFlbHQycHBobDFzN2RjMXAifQ.yp1dgX8hJcZM1r9Tq7eW2A"
}

##
# DEFAULT VALUES
##

DEFAULT_YEAR = 2010

##
# LOAD DATA
##

data = load_data()
filtered_data = filter_by_year(data, DEFAULT_YEAR)

##
# MAP
##


scatter = go.Scattermapbox(
    lat=[],
    lon=[],
    mode='markers+text',
    textposition='middle center',
    textfont=dict(size=14, color=custom_color_text_color_blue),
    marker=go.scattermapbox.Marker(
        size=50,
        color=custom_color_yellow,
        symbol="circle",
        opacity=0.5
    ),
    text=[],
    hoverinfo="none",  # or "text" ?
    hovertext=[],
    hoverlabel=go.scattermapbox.Hoverlabel(
        bgcolor=custom_color_yellow,
        bordercolor=custom_color_yellow,
        font={"family": "Noto Sans KR", "color": custom_color_text_color_blue}
    )
)

map = go.Figure(scatter, layout=go.Layout(
    uirevision=True,
    autosize=True,
    hovermode='closest',
    mapbox=dict(
        accesstoken=mapbox["token"],
        bearing=-5,
        center=dict(
            lat=47.99597060066705,
            lon=7.856035275762166
        ),
        pitch=80,
        zoom=15,
        style=mapbox["style"]
    ),
    margin={"r": 0, "t": 0, "l": 0, "b": 0}  # this maxes the map full screen
))

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
    value=DEFAULT_YEAR,
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
    [Output('slider_output', 'children'), Output('freiburg_map', 'figure')],
    Input('time_axis', 'value'))
def update_slider(value):
    global filtered_data

    filtered_data = filter_by_year(filtered_data, int(value))

    lat = []
    long = []
    text = []
    for place in filtered_data["places"]:
        lat.append(str(place["location"]["lat"]))
        long.append(str(place["location"]["long"]))
        text.append(place["name"])

    map.update_traces({"lat": lat, "lon": long, "text": text, "hovertext": text})
    map.update_traces(uirevision="some-constant")

    return 'You have selected the year "{}"'.format(value), map


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
