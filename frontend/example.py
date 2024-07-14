import time

from backend.api import ble_connection, retrieve_data
import dash
from dash import html, callback, dcc, no_update, clientside_callback
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

figure = dict(data=[{'Time_sec': [], 'Signal': []}], layout=dict(xaxis=dict(range=[-1, 10000]), yaxis=dict(range=[2000, 4000])))

app.layout = html.Div([
    # dcc: Dash Core Components
    dcc.Markdown(''' #### Wearout Dashboard'''),
    html.Button("Connect to Wearout", id="button_connect"),
    html.Div(children="Waiting to connect...", id="retrieve_data_from_connect"),
    html.Div(children="Waiting to retrieve data...", id="data_output", hidden=True),
    dcc.Graph(id='graph', figure=dict(figure)),
    dcc.Interval(id="interval", interval=130, n_intervals=0),
    #dcc.Store(id='offset', data=0),
    dcc.Store(id='store', data=dict(Time_sec=[], Signal=[], resolution=resolution)),
])


@callback(Output("interval", "n_intervals"), Input("button_connect", "n_clicks"), prevent_initial_call=True)
def connection_callback(n):
    bool_connect = ble_connection()
    if not bool_connect:
        raise PreventUpdate
    # TODO: Do I need the return?
    return 1


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
