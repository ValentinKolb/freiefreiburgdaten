import json
import os
from typing import TypeVar
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from data_tools import load_data, filter_by_year, filter_by_category, pprint_dict, get_categories
from styles import *
import pandas as pd

# Create main process
app = dash.Dash(__name__)

mapbox = {
    "style": "mapbox://styles/valentinkolb/cksjew54g1s4t18s063qaku5k",
    "token": "pk.eyJ1IjoidmFsZW50aW5rb2xiIiwiYSI6ImNrczdtb3ZvNzFlbHQycHBobDFzN2RjMXAifQ.yp1dgX8hJcZM1r9Tq7eW2A"
}

##
# DEFAULT VALUES
##

DEFAULT_YEAR = 2010
DEFAULT_MAP_ZOOM = 15.5

##
# LOAD DATA
##

unfiltered_data = load_data()

##
# MAP
##


scatter = go.Scattermapbox(
    lat=[],
    lon=[],
    mode='markers+text',
    textposition='middle center',
    textfont={"size": 15, "color": custom_color_text_color_blue},
    marker=go.scattermapbox.Marker(
        size=10,
        color=custom_color_text_color_blue,
        symbol="circle",
        opacity=.9
    ),
    text=[],
    hoverinfo="text",  # or "text" ?
    hovertext=[],
    hoverlabel=go.scattermapbox.Hoverlabel(
        bgcolor=custom_color_yellow,
        bordercolor=custom_color_yellow,
        font={"family": "Noto Sans KR",
              "color": custom_color_text_color_blue,
              "size": 15}
    )
)

map = go.Figure(
    data=scatter,
    layout=go.Layout(
        clickmode='event',
        uirevision=True,
        autosize=True,
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox["token"],
            bearing=-5,
            center=dict(
                lat=47.99461758304593,
                lon=7.8538004648156825
            ),
            pitch=80,
            zoom=DEFAULT_MAP_ZOOM,
            style=mapbox["style"]
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 0}  # this maxes the map full screen
    ))

##
# DROPDOWN
##


filter_dropdown = dcc.Dropdown(
    id="filter_dropdown",
    options=[],
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

    # this stores the data (graph data) of the current session and resets if the page reloads
    dcc.Store(id='session', storage_type='memory'),

    html.H1("Freiburg", id="header"),

    dcc.Graph(id='freiburg_map', figure=map),

    html.Div(id="dropdown_area", children=[filter_dropdown]),

    html.Div(id="time_slider", children=[time_axis]),

    html.Div(id="content_area", children=[

        html.Div(id="content", children=[
            html.Div(id='test_output_1'),
            html.Div(id='test_output_2')
        ]),

    ])
])


##
# INTERACTIVITY
##


@app.callback(
    [Output('test_output_1', 'children'),
     Output('test_output_2', 'children'),
     Output('freiburg_map', 'figure'),
     Output('filter_dropdown', 'options'),
     Output('session', 'data')],
    [Input('freiburg_map', 'relayoutData'),
     Input('freiburg_map', 'clickData'),
     Input('header', 'n_clicks'),
     Input('filter_dropdown', 'value'),
     Input('time_axis', 'value')],
    [State('test_output_1', 'children'),
     State('test_output_2', 'children'),
     State("freiburg_map", "figure"),
     State('filter_dropdown', 'options'),
     State('session', 'data')]
)
def interact(_, map_click, header_click, category_filter, year_filter,
             test_output_1_state, test_output_2_state, map_state, filter_dropdown_state, data_state):
    startup = not bool(data_state)
    data_changed = False

    # case time slider
    if startup or dash.callback_context.triggered[0]['prop_id'] == 'time_axis.value':
        data_state = filter_by_year(unfiltered_data, year_filter)
        filter_dropdown_state = [{"label": f'{cat}', "value": f'{cat}'} for cat in get_categories(data_state)]
        data_changed = True

    # case filter dropdown
    if dash.callback_context.triggered[0]['prop_id'] == 'filter_dropdown.value' and category_filter:
        data_state = filter_by_category(data_state, category_filter)
        data_changed = True

    # case map zoom
    if dash.callback_context.triggered[0]['prop_id'] == 'freiburg_map.relayoutData':
        current_zoom = map_state["layout"]["mapbox"]["zoom"]
        if current_zoom >= DEFAULT_MAP_ZOOM:
            map.update_traces({"mode": 'text', "hoverinfo": "none"})
        else:
            map.update_traces({"mode": 'markers', "hoverinfo": "text"})

    # case click on header
    if dash.callback_context.triggered[0]['prop_id'] == 'header.n_clicks':
        test_output_2_state = (None,)

    # case map click
    if dash.callback_context.triggered[0]['prop_id'] == 'freiburg_map.clickData':
        location = map_click['points'][0]['text']

        test_output_2_state = select_location(location=location, data_state=data_state,
                                              map=map, output=test_output_2_state)

    # only redraw map if data has changed
    if data_changed:
        lat = []
        long = []
        text = []
        for place in data_state["places"]:
            lat.append(str(place["location"]["lat"]))
            long.append(str(place["location"]["long"]))
            text.append(place["name"])
        map.update_traces({"lat": lat, "lon": long, "text": text, "hovertext": text})

    # test_output_1_state = f'year-slider: {year_filter}, category-dropdown: {category_filter}'

    return test_output_1_state, test_output_2_state, map, filter_dropdown_state, data_state


def select_location(location, data_state: dict, map: go.Figure, output) -> list:
    selected_data = [place for place in data_state["places"] if place["name"] == location][0]
    # pprint_dict(selected_data)
    # map.update_layout(mapbox={'center': {"lat": selected_data["location"]["lat"],
    # "lon": selected_data["location"]["long"]}})  # center map ?? todo ??

    output_children = []

    output_children.append(html.H1(selected_data["name"]))
    output_children.extend([html.H4(cat) for cat in selected_data["category"]])
    output_children.append(html.Div(id='location_description', children=[selected_data["description"]["description"]]))
    output_children.append(html.A('source', href=selected_data["description"]["source"]))

    for datasheet in selected_data["data"]:
        s = render_data(datasheet)

        output_children.append(html.Div(children=[s]))




    return output_children  # f'{json.dumps(selected_data, indent=4, ensure_ascii=False)}',


def render_data(data: dict) -> object:
    path = data["dataSheet"]
    separator = data["separator"]

    print(path)

    # with open('src/data/datasheets/Theater/Aufführungen und Besucher im Wallgrabentheater Freiburg.csv',

    #         encoding="ISO-8859-1") as file:
    #  print(file.read())
    df = pd.read_csv(filepath_or_buffer=path, delimiter=separator, encoding="ISO-8859-1")
    print(df)
    return str(df)

    # data/datasheets/Kultur/Konzerthaus Freiburg - Besucher.csv
    # data/Kultur/Konzerthaus Freiburg - Besucher.csv
    # data/datasheets/Theater/Aufführungen und Besucher im Wallgrabentheater Freiburg.csv


##
# START PROGRAM
##

if __name__ == '__main__':
    app.run_server(debug=True)
