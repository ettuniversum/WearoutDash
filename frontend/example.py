import time

from backend.api import ble_connection, retrieve_data
import dash
from dash import html, callback, dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import numpy as np
import datetime

# Example data (a circle).
Fs = 8000
f = 50
resolution = 10000 # sample
x = np.array([datetime.datetime.now(), datetime.datetime.now()])
y = np.array([3000, 3000+1])

app = dash.Dash(__name__, update_title=None)  # remove "Updating..." from title

figure = dict(data=[{'x': [], 'y': []}], layout=dict(xaxis=dict(range=[-1, 10000]), yaxis=dict(range=[2000, 4000])))

app.layout = html.Div([
    # dcc: Dash Core Components
    dcc.Markdown(''' #### Wearout Dashboard'''),
    html.Button("Connect to Wearout", id="button_connect"),
    html.Div(children="Waiting to connect...", id="retrieve_data_from_connect"),
    html.Div(children="Waiting to retrieve data...", id="data_output", hidden=True),
    dcc.Graph(id='graph', figure=dict(figure)),
    dcc.Interval(id="interval", interval=10000, n_intervals=0),
    #dcc.Store(id='offset', data=0),
    dcc.Store(id='store', data=dict(x=x, y=[], resolution=resolution)),
])

#
# Local Client Callback - Super Fast
# Resource: https://stackoverflow.com/questions/63589249/plotly-dash-display-real-time-data-in-smooth-animation
# app.clientside_callback(
#     """
#     function (n_intervals, data, offset) {
#         offset = offset % data.x.length;
#         const end = Math.min((offset + 10), data.x.length);
#         return [[{x: [data.x.slice(offset, end)], y: [data.y.slice(offset, end)]}, [0], 500], end]
#     }
#     """,
#     [Output('graph', 'extendData'), Output('offset', 'data')],
#     [Input('interval', 'n_intervals')],
#     [State('store', 'data'), State('offset', 'data')]
# )


# @callback(
#     Output("store", "data"),
#     Input("button_connect", "n_clicks"), prevent_initial_call=True)
# def connection_callback(n):
#     df_data = ble_connection()
#     print('First time getting data...')
#     print(df_data.to_dict())
#     x = df_data['Time_sec']
#     y = df_data['Signal']
#     data_dict = dict(x=x, y=y, resolution=resolution)
#     return data_dict


@app.callback(Output('store', 'data'), Input("interval", "n_intervals"))
def gen_signal_dataframe(interval):
    '''
    Update the data graph
    :param interval:  Update the graph based on an interval
    :return: dictionary
    '''
    try:
        df_data = ble_connection()
        print('First time getting data...')
        x = str(df_data['Time_sec'][0])
        #x = np.array([datetime.datetime.now(), datetime.datetime.now()])
        y = int(df_data['Signal'][0])
        data_dict = dict(x=[x], y=[y], resolution=resolution)
        print(data_dict)
        return data_dict
    except:
        raise PreventUpdate


@app.callback(Output('graph', 'figure'), Input('store', 'data'))
def on_data_set_graph(data):
    print('>>> Updating graph...')
    print(data)
    return {'data': [data]}





if __name__ == '__main__':
    # Service the dashboard last
    app.run_server(debug=False)
