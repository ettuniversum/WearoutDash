import asyncio

import pandas as pd

from backend.BLEInterface import BLEInterface
import dash
from dash import html
from dash import dcc
import numpy as np
from dash.dependencies import Input, Output, State

from threading import Thread


# Example data (a circle).
Fs = 8000
f = 50
resolution = 10000 # sample
#time = np.linspace(0, np.pi * 2, resolution)
x = np.arange(resolution)
y = np.sin(2 * np.pi * f * x / Fs)
#print(len(x))
#print(len(y))



# custom thread
class BLEThread(Thread):
    # constructor
    def __init__(self):
        # execute the base constructor
        Thread.__init__(self)
        # set a default value
        self.df_signal = None
        self.ble_interface = BLEInterface("F4:12:FA:5A:81:D1")
        bool_found = self.ble_interface.found_device()
        if bool_found:
            bool_connect = self.ble_interface.setup_connection()
            if bool_connect:
                self.connected = True
            else:
                self.connected = False

    # function executed in a new thread
    def run(self):
        if self.connected:
            # Init sample
            df_sample = pd.DataFrame([])
            for i in range(100):
                df_signal = self.ble_interface.read_gatt()
                df_sample = pd.concat([df_sample, df_signal])
            df_sample = df_sample.reset_index(drop=True)
            self.df_signal = df_sample

#def update_app_graph(thread):
    # Pull data from the thread
    # Update the store with the data



if __name__ == '__main__':
    thread = BLEThread()
    thread.start()
    thread.join()
    data = thread.df_signal
    print(data.columns)
    print(data)
    x = data['Time_sec']
    y = data['Signal']
    thread.ble_interface.close_connection()
    figure = dict(data=[{'x': [], 'y': []}], layout=dict(xaxis=dict(range=[-1, 10000]), yaxis=dict(range=[2000, 4000])))
    app = dash.Dash(__name__, update_title=None)  # remove "Updating..." from title



    app.layout = html.Div([
        # dcc: Dash Core Components
        dcc.Markdown(''' #### Wearout Dashboard'''),
        dcc.Graph(id='graph', figure=dict(figure)), dcc.Interval(id="interval", interval=1),
        dcc.Store(id='offset', data=0), dcc.Store(id='store', data=dict(x=x, y=y, resolution=resolution)),
    ])
    # Callback for looping locally with chunks of data
    app.clientside_callback(
        """
        function (n_intervals, data, offset) {
            offset = offset % data.x.length;
            const end = Math.min((offset + 10), data.x.length);
            return [[{x: [data.x.slice(offset, end)], y: [data.y.slice(offset, end)]}, [0], 500], end]
        }
        """,
        [Output('graph', 'extendData'), Output('offset', 'data')],
        [Input('interval', 'n_intervals')], [State('store', 'data'), State('offset', 'data')]
    )
    # Service the dashboard last
    app.run_server(debug=True)
