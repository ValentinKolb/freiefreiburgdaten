import logging
import os

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from data_tools import filter_by_year, filter_by_category, get_categories
from file_tools import load_file_cached, load_meta_data, load_csv_file_cached
from styles import *
from textwrap import wrap

# Create main process
app = dash.Dash(name='freiefreiburgdaten')

mapbox = {
    "style": "mapbox://styles/valentinkolb/cksjew54g1s4t18s063qaku5k",
    "token": "pk.eyJ1IjoidmFsZW50aW5rb2xiIiwiYSI6ImNrczdtb3ZvNzFlbHQycHBobDFzN2RjMXAifQ.yp1dgX8hJcZM1r9Tq7eW2A"
}

##
# LOGGING
##

LOGGER = app.logger
[LOGGER.removeHandler(hdlr) for hdlr in LOGGER.handlers]

_LOGGING_STDOUT_FORMAT = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s',
                                           datefmt='%H:%M:%S')
_LOGGING_STDOUT_HANDLER = logging.StreamHandler()
_LOGGING_STDOUT_HANDLER.setFormatter(_LOGGING_STDOUT_FORMAT)

LOGGER.addHandler(_LOGGING_STDOUT_HANDLER)

##
# LOAD DATA
##

unfiltered_data = load_meta_data()
LOGGER.info("meta.json loaded")

##
# DEFAULT VALUES
##

DEBUG = os.environ.get('DASH_DEBUG', True)
LOGGER.setLevel(logging.DEBUG if DEBUG else logging.INFO)

DEFAULT_YEAR = 2010
DEFAULT_MAP_ZOOM = 15.5
DEFAULT_MAP_LAT = unfiltered_data["default"]["location"]["lat"]
DEFAULT_MAP_LONG = unfiltered_data["default"]["location"]["long"]
TITLE = unfiltered_data["default"]["name"]

##
# MAP
##

scatter = go.Scattermapbox(
    lat=[],
    lon=[],
    mode='markers+text',
    textposition='top center',
    textfont={"size": 15, "color": custom_color_text_color_blue},
    marker=go.scattermapbox.Marker(
        size=10,
        color=custom_color_text_color_blue,
        symbol="circle",
        opacity=.9
    ),
    text=[],
    hoverinfo="text",
    hovertext=[],
    hoverlabel=go.scattermapbox.Hoverlabel(
        bgcolor=custom_color_yellow,
        bordercolor=custom_color_yellow,
        font={"family": "Noto Sans KR",
              "color": custom_color_text_color_blue,
              "size": 15}
    )
)

scatter_data = {
    "mode": 'markers+text',
    "textposition": 'top center',
    "textfont": {"size": 15, "color": custom_color_text_color_blue},
    "marker": go.scattermapbox.Marker(
        size=10,
        color=custom_color_text_color_blue,
        symbol="circle",
        opacity=.9
    ),
    "hoverlabel": go.scattermapbox.Hoverlabel(
        bgcolor=custom_color_yellow,
        bordercolor=custom_color_yellow,
        font={"family": "Noto Sans KR",
              "color": custom_color_text_color_blue,
              "size": 15}
    )
}

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
                lat=DEFAULT_MAP_LAT,
                lon=DEFAULT_MAP_LONG
            ),
            pitch=80,
            zoom=DEFAULT_MAP_ZOOM,
            style=mapbox["style"]
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    ))

##
# DROPDOWN
##


filter_dropdown = dcc.Dropdown(
    id="filter_dropdown",
    options=[],
    value=[],
    multi=True,
    placeholder="Filtere die Orte ..."
)

##
# SLIDER
##

time_axis = dcc.Slider(
    id='time_axis',
    min=1900,
    max=2021,
    value=DEFAULT_YEAR,
    marks={year: {'label': str(year)} for year in range(1900, 2022, 10)},
    included=False
)

##
# MAIN APP LAYOUT
##

app.layout = html.Div([

    # this stores the data (graph data) of the current session and resets if the page reloads
    dcc.Store(id='session', storage_type='memory'),

    html.H1(TITLE, id="header"),

    dcc.Graph(id='freiburg_map',
              figure=map,
              config={
                  'displayModeBar': False
              }),

    html.Div(id="dropdown_area", children=[filter_dropdown]),

    html.Div(id="time_slider", children=[time_axis]),

    html.Button("?", id="about_button"),

    html.Button("🐛", id="debug_button", style={"opacity": 1 if DEBUG else 0}),

    html.Div(className="message_box", id="about_section", children=[]),
    html.Div(className="message_box", id="debug_message", children=[]),

    html.Div(id="content_area", children=[

        html.Div(id="content", children=[
            html.Div(id='debug_output'),
            html.Div(id=' data_visualisation')
        ]),

    ])
])


##
# INTERACTIVITY
##

@app.callback(
    [Output('debug_button', 'children')],
    [Input('debug_button', 'n_clicks')],
    prevent_initial_call=True
)
def debug_action(_) -> tuple:
    """
    this callback function displays the about/ help text if the user clicks on the corresponding button

    Parameters
    ----------
    _ :
        the number of times the button was clicked, is ignored

    Returns
    -------
    tuple :
        the first value is the about text, the second value the button text
        and the third value the style of the about section (is used to hide it)
    """
    global unfiltered_data
    load_csv_file_cached.cache_clear()
    load_file_cached.cache_clear()
    app.logger.debug("all file caches cleared!")
    unfiltered_data = load_meta_data()
    app.logger.debug("meta.json was reloaded!")
    return "🐛",


@app.callback(
    [Output('about_section', 'children'),
     Output('about_button', 'children'),
     Output('about_section', 'style')],
    [Input('about_button', 'n_clicks')],
    [State('about_button', 'children')],
    prevent_initial_call=True
)
def display_about(_, button_text) -> tuple:
    """
    this callback function displays the about/ help text if the user clicks on the corresponding button

    Parameters
    ----------
    _ :
        the number of times the button was clicked, is ignored
    button_text :
        the current text of the button

    Returns
    -------
    tuple :
        the first value is the about text, the second value the button text
        and the third value the style of the about section (is used to hide it)
    """
    if button_text == "?":
        button_text = "X"
        about = dcc.Markdown(load_file_cached(file="data/HowTo.md"))
        style = {'opacity': 1}
    else:
        button_text = "?"
        about = None
        style = {'opacity': 0}

    return about, button_text, style


@app.callback(
    [Output('debug_output', 'children'),
     Output(' data_visualisation', 'children'),
     Output('freiburg_map', 'figure'),
     Output('filter_dropdown', 'options'),
     Output('session', 'data')],
    [Input('freiburg_map', 'relayoutData'),
     Input('freiburg_map', 'clickData'),
     Input('header', 'n_clicks'),
     Input('filter_dropdown', 'value'),
     Input('time_axis', 'value')],
    [State('debug_output', 'children'),
     State(' data_visualisation', 'children'),
     State("freiburg_map", "figure"),
     State('filter_dropdown', 'options'),
     State('session', 'data')]
)
def interact(_, map_click, __, category_filter, year_filter,
             debug_output, data_visualisation, map_state, filter_dropdown_state, data_state) -> tuple:
    """
    this single callback function provides all interactivity for the application.

    it takes as input all elements on which events it responds. it also takes the state of all elements
    it changes. this state will only be modified if the corresponding event was triggert.

    which event the user triggert is stored in the dash.callback_context.triggered[0]['prop_id'] variable
    which is queried.

    Parameters
    ----------
    _ :
        this input in ignored. the 'Input('freiburg_map', 'relayoutData')' is only listed so that this function
        is notified if the user zooms on the map.
    map_click :
        this variable holds the last clicked location on the map.
    __ :
        this input is also ignored. the 'Input('header', 'n_clicks')' is only listed so that this function is
        notified if the user clicks on the header.
    category_filter :
        this variable holds the currently selected categories.
    year_filter :
        this variable holds the currently selected year.
    debug_output :
        this is the state of the first text output. this is only used for debug purposes.
    data_visualisation :
        this is the state of the second text output. this holds the data for the selected location.
    map_state :
        this is the state of the map. this holds for example the current zoom value. this state is
        modified to display the correct ticks an their hover info.
    filter_dropdown_state :
        this state is modified to adjust the selectable category filters
    data_state :
        this is the data the user selected in the current session. this will be cleared if the page is reloaded

    Returns
    -------
    tuple :
        the first value is the debug output, the second value is the content visualizing the data, the third
        value is the (updated) map state, the fourth value is the (updated) category filter state and the fifth
        value is the selected data by the user

    """

    startup = not bool(data_state)
    data_changed = False

    # case time slider
    if startup or dash.callback_context.triggered[0]['prop_id'] == 'time_axis.value':
        data_state = filter_by_year(unfiltered_data, year_filter)
        filter_dropdown_state = [{"label": f'{cat}', "value": f'{cat}'} for cat in get_categories(data_state)]
        data_changed = True

    # case filter dropdown
    if dash.callback_context.triggered[0]['prop_id'] == 'filter_dropdown.value':
        data_changed = True
        if category_filter:
            data_state = filter_by_category(data_state, category_filter)
        else:
            data_state = filter_by_year(unfiltered_data, year_filter)

    # case map zoom
    current_zoom = map_state["layout"]["mapbox"]["zoom"]
    if dash.callback_context.triggered[0]['prop_id'] == 'freiburg_map.relayoutData':
        data_changed = True
        if current_zoom >= DEFAULT_MAP_ZOOM:
            map.update_traces({"mode": 'markers+text', "hoverinfo": "text"})
        else:
            map.update_traces({"mode": 'markers', "hoverinfo": "text"})

    # case click on header
    if startup or dash.callback_context.triggered[0]['prop_id'] == 'header.n_clicks':
        data_visualisation = render_location(location_data=unfiltered_data["default"])

    # case map click
    if dash.callback_context.triggered[0]['prop_id'] == 'freiburg_map.clickData':
        location = map_click['points'][0]['text']

        data_visualisation = render_location(
            location_data=[place for place in data_state["places"] if place["name"] == location][0])

    # only redraw map if data has changed
    if data_changed:
        lat = []
        long = []
        text = []
        hover_text = []
        for place in data_state["places"]:
            lat.append(str(place["location"]["lat"]))
            long.append(str(place["location"]["long"]))
            text.append(place["name"])
            short_description = '<br>'.join(wrap(place["description"]["shortDescription"], width=30))
            hover_text.append(short_description)
        map.update_traces({"lat": lat, "lon": long, "text": text})
        map.update_traces({"hovertext": text if current_zoom < DEFAULT_MAP_ZOOM else hover_text})

    # debug_output = f'year-slider: {year_filter}, category-dropdown: {category_filter}'

    return debug_output, data_visualisation, map, filter_dropdown_state, data_state


def render_location(location_data: dict) -> list:
    """
    this functions renders the visualisation output for a selected location
    Parameters
    ----------
    location_data : dict
        the data for the selected location. this data will be visualised

    Returns
    -------
    list :
        a list of html elements to the displayed
    """

    output_children = []

    output_children.append(html.H1(location_data["name"]))
    output_children.append(html.Div(id='categories', children=[html.H4(cat) for cat in location_data["category"]]))

    output_children.append(
        html.A('Quelle Beschreibung ..', href=location_data["description"]["source"], target='_blank'))
    output_children.append(
        render_description(location_data["description"]["description"])
    )

    for datasheet in location_data["data"]:
        s = render_data(datasheet)
        output_children.extend(s)

    return output_children


def render_description(description_path: str) -> dcc.Markdown:
    """
    this functions return the description of a location as Markdown element.

    Parameters
    ----------
    description_path : str
        the path of the file containing the markdown

    Returns
    -------
    dcc.Markdown :
        a markdown element
    """
    description = load_file_cached(description_path)
    return dcc.Markdown(description, id="location_description")


def render_data(data: dict) -> tuple:
    """
    this functions renders a csv file as graph

    Parameters
    ----------
    data : dict
        the dict containing the meta data for the datasheet

    Returns
    -------
    dcc.Graph :
        the assembled graph
    """
    identifier = data["identifier"]
    graph_type = data["graph"]["type"]
    add_args = {}
    if graph_type == "line":
        graph_class = go.Scatter
    elif graph_type == "bar":
        graph_class = go.Bar
    elif graph_type == "funnel":
        graph_class = go.Funnel
    elif graph_type == "scatter":
        graph_class = go.Scatter
        add_args = add_args | {"mode": 'markers'}
    elif graph_type == "histogram":
        graph_class = go.Histogram
    else:
        return html.Div(f'An error occurred, invalid graph type: {graph_type!r}', style={"color": "red"}),

    data_dict = load_csv_file_cached(data["dataSheet"], delimiter=data["delimiter"], encoding=data["encoding"])

    keys = list(data_dict.keys())
    x = keys[0]
    ys = keys[1:]

    fig = go.Figure()
    fig.update_layout(legend={
        "orientation": "h",
        "yanchor": "bottom",
        "y": 1,
        "xanchor": "right",
        "x": 1

    },
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title=x,
    )

    for y in ys:
        fig.add_trace(graph_class(
            x=data_dict[x],
            y=data_dict[y],
            name=y,
            **add_args
        ))

    return (html.H2(identifier),
            html.A("Quelle Daten ..", href=data["sourceLink"], target='_blank'),
            dcc.Graph(figure=fig, config={
                'displayModeBar': False
            }),
            )

##
# START PROGRAM
##

if __name__ == '__main__':
    try:
        app.run_server(debug=DEBUG)
    except Exception as e:
        LOGGER.exception(f"a critcal exception uccured: {e}")
        LOGGER.info("the server is stopped due to an exception")
