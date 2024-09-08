import time

from backend.api import ble_connection, retrieve_data
import dash
from dash import html, callback, dcc, no_update, clientside_callback
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import datetime
import heartpy as hp
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from scipy.signal import resample


# Example data (a circle).
Fs = 8000
f = 50
resolution = 10000 # sample
x = np.array([datetime.datetime.now(), datetime.datetime.now()])
y = np.array([3000, 3000+1])

##### FIG LAYOUT
font_style = {
    'color' : '#f6f6f6'
}

margin_style = {
    'b': 20,
    'l': 50,
    'r': 8,
    't': 50,
    'pad': 0
}

xaxis_style = {
    'linewidth' : 1,
    'linecolor' : 'rgba(0, 0, 0, 0.35%)',
    'showgrid' : False,
    'zeroline' : False
}

yaxis_style = {
    'linewidth' : 1,
    'linecolor' : 'rgba(0, 0, 0, 0.35%)',
    'showgrid' : True,
    'gridwidth' : 1,
    'gridcolor' : 'rgba(0, 0, 0, 0.11%)',
    'zeroline' : False
}

my_figlayout = go.Layout(
    paper_bgcolor='rgba(0,0,0,0)', # Figure background is transparend and controll by css on dcc.Graph() components
    plot_bgcolor='rgba(0,0,0,0)',
    font = font_style,
    margin = margin_style,
    xaxis = xaxis_style,
    yaxis = yaxis_style,
    height = 300
)

app = dash.Dash(__name__, update_title=None)  # remove "Updating..." from title
app.title = "Wearout"
figure = dict(data=[{'Time_sec': [], 'Signal': [], 'type':'line','name':'Cases','line':dict(color='white')}], layout=my_figlayout)

app.layout = html.Div([
    # dcc: Dash Core Components
    dcc.Markdown(''' #### Wearout Dashboard'''),
    html.Button("Connect to Wearout", id="button_connect"),
    html.Div(children="Waiting to connect...", id="retrieve_data_from_connect"),
    html.A(
        html.Img(
            src=app.get_asset_url("CG_heart_2.gif"),
            className="app__menu__img",
        ),
        href="https://plotly.com/dash/",
    ),
    dcc.Graph(id='graph', figure=dict(figure)),
    html.Div(children="Waiting for more data...", id="display_bpm", style={'display': 'inline-block'}),
    html.A(
        html.Img(
            src=app.get_asset_url("ObrigadoGif.gif"),
            className="app__menu__img",
        ),
        href="https://plotly.com/dash/",
        style={'display': 'inline-block'},
    ),
    dcc.Interval(id="interval", interval=130, n_intervals=0),
    dcc.Store(id='store', data=dict(Time_sec=[], Signal=[], resolution=resolution)),
    dcc.Store(id='store_measures', data=dict(bpm=None, ibi=None, sdnn=None, sdsd=None, rmssd=None, pnn20=None,
                                             pnn50=None, hr_mad=None, sd1=None, sd2=None, s=None, sd1_sd2=None,
                                             breathingrate=None)),
])


@callback(Output("retrieve_data_from_connect", "children"), Input("button_connect", "n_clicks"), prevent_initial_call=True)
def connection_callback(n):
    bool_connect = ble_connection()
    if not bool_connect:
        return "Reset device. Try Again."
    return "Connected."


@callback(Output('store', 'data'), Input('interval', 'n_intervals'), State('store', 'data'), prevent_initial_call=True)
def update_store(n_clicks, data_store):
    # Retrieve new data
    new_df = retrieve_data()
    if new_df.empty:
        raise PreventUpdate
    # Extract new x and y values
    new_x = new_df['Time_sec'].tolist()
    new_y = new_df['Signal'].tolist()
    # Extend existing data with new data
    extended_data = {
        'Time_sec': data_store['Time_sec'] + new_x,
        'Signal': data_store['Signal'] + new_y,
        'resolution': data_store['resolution']
    }
    return extended_data


app.clientside_callback(
    """
    function(data, existing_figure) {
        // Create a copy of the existing figure
        const new_figure = JSON.parse(JSON.stringify(existing_figure));

        // Update only the data portion
        new_figure.data[0].x = data.Time_sec;
        new_figure.data[0].y = data.Signal;

        return new_figure;
    }
    """,
    Output('graph', 'figure'),
    Input('store', 'data'),
    State('graph', 'figure'),
    prevent_initial_call=True
)


@callback(Output('store_measures', 'data'), Input('interval', 'n_intervals'), State('store', 'data'), prevent_initial_call=True)
def detect_bpm(n_intervals, data_store):
    data = np.array(data_store['Signal'])
    if len(data) < 50:
       return no_update
    timer = data_store['Time_sec']
    sample_rate = hp.get_samplerate_datetime(timer, timeformat='%Y-%m-%dT%H:%M:%S.%f')
    ## Clean up the raw data
    filtered_ppg = hp.filter_signal(data[0:int(240 * sample_rate)],
                                    cutoff=[0.8, 2.5],
                                    filtertype='bandpass',
                                    sample_rate=sample_rate,
                                    order=3,
                                    return_top=False)
    resampled = resample(filtered_ppg, len(filtered_ppg) * 10)
    new_sample_rate = sample_rate * 10
    working_data, measures = hp.process(resampled, sample_rate=new_sample_rate, high_precision=True, clean_rr=True)
    return measures


@callback(Output('display_bpm', 'children'), Input('store_measures', 'data'), prevent_initial_call=True)
def update_value_display(measure_data):
    if not measure_data or not measure_data['bpm']:
        return "No data available"

    # Get the most recent processed value
    latest_value = measure_data['bpm']

    # Format the display string
    display_string = f"BPM: {latest_value:.2f}"

    return display_string

if __name__ == '__main__':
    # Service the dashboard last
    app.run_server(debug=False)
