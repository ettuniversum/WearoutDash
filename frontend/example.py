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
from scipy.signal import resample


# Example data (a circle).
Fs = 8000
f = 50
resolution = 10000 # sample
x = np.array([datetime.datetime.now(), datetime.datetime.now()])
y = np.array([3000, 3000+1])

app_color = {"graph_bg": "#082255", "graph_line": "#007ACE"}

app = dash.Dash(__name__, update_title=None)  # remove "Updating..." from title
app.title = "Wearout"
figure = dict(data=[{'Time_sec': [], 'Signal': []}], layout=dict(xaxis=dict(range=[-1, 10000]), yaxis=dict(range=[2000, 4000]), plot_bgcolor=app_color["graph_bg"], paper_bgcolor=app_color["graph_bg"]))

app.layout = html.Div([
    # dcc: Dash Core Components
    dcc.Markdown(''' #### Wearout Dashboard'''),
    html.Button("Connect to Wearout", id="button_connect"),
    html.Div(children="Waiting to connect...", id="retrieve_data_from_connect"),
    html.Div(children="Waiting to retrieve data...", id="data_output", hidden=True),
    html.A(
        html.Img(
            src=app.get_asset_url("CG_heart_2.gif"),
            className="app__menu__img",
        ),
        href="https://plotly.com/dash/",
    ),
    dcc.Graph(id='graph', figure=dict(figure)),
    dcc.Interval(id="interval", interval=130, n_intervals=0),
    dcc.Store(id='store', data=dict(Time_sec=[], Signal=[], resolution=resolution)),
])


@callback(Output("retrieve_data_from_connect", "children"), Input("button_connect", "n_clicks"), prevent_initial_call=True)
def connection_callback(n):
    bool_connect = ble_connection()
    if not bool_connect:
        raise PreventUpdate
    # TODO: Do I need the return?
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


# @callback(Output('store', 'data'), Input('store', 'data'), prevent_initial_call=True)
# def detect_bpm(n_clicks, data_store):
#     data = np.array(data_store['Signal'])
#     timer = data_store['Time_sec']
#     sample_rate = hp.get_samplerate_datetime(timer, timeformat='%Y-%m-%dT%H:%M:%S.%f')
#     # Clean up the raw data
#     filtered_ppg = hp.filter_signal(data[0:int(240 * sample_rate)],
#                                     cutoff=[0.8, 2.5],
#                                     filtertype='bandpass',
#                                     sample_rate=sample_rate,
#                                     order=3,
#                                     return_top=False)
#     resampled = resample(filtered_ppg, len(filtered_ppg) * 10)
#     new_sample_rate = sample_rate * 10
#     for s in [[0, 10000], [10000, 20000], [20000, 30000], [30000, 40000], [40000, 50000]]:
#         wd, m = hp.process(resampled[s[0]:s[1]], sample_rate=new_sample_rate,
#                            high_precision=True, clean_rr=True)
#         hp.plotter(wd, m, title='zoomed in section', figsize=(12, 6))
#         hp.plot_poincare(wd, m)
#         plt.show()
#         for measure in m.keys():
#             print('%s: %f' % (measure, m[measure]))


app.clientside_callback(
    """
    function(data) {
        return {
            'data': [{
                'x': data.Time_sec,
                'y': data.Signal,
                'type': 'scatter'
            }],
            'layout': {
                'title': 'Updated Figure'
            }
        };
    }
    """,
    Output('graph', 'figure'),
    Input('store', 'data'),
    prevent_initial_call=True
)


if __name__ == '__main__':
    # Service the dashboard last
    app.run_server(debug=False)
