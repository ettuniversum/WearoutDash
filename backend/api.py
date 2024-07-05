import pandas as pd

from .BLEInterface import BLEInterface
from threading import Thread
from pandas import DataFrame, concat


class BLEThread(Thread):
    # constructor
    def __init__(self):
        # execute the base constructor
        Thread.__init__(self, name="F4:12:FA:5A:81:D1")
        # set a default value
        self.df_signal = None
        print('Thread creation...')
        self.ble_interface = BLEInterface("F4:12:FA:5A:81:D1")
        self.connected = True
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
            df_sample = DataFrame([])
            df_signal = self.ble_interface.read_gatt()
            print('Thread run data results...')
            print(df_signal)
            df_sample = concat([df_sample, df_signal])
            df_sample = df_sample.reset_index(drop=True)
            self.df_signal = df_sample


ble_interface = BLEInterface("F4:12:FA:5A:81:D1")


def ble_connection():
    bool_found = ble_interface.found_device()
    # If we found the device, then we haven't connected to it
    if bool_found:
        bool_connect = ble_interface.setup_connection()
        return bool_connect
        # if bool_connect:
        #     df_signal = ble_interface.read_gatt()
        #     return df_signal
    # elif ble_interface.connected:
    #     df_signal = ble_interface.read_gatt()
    #     # df_append = pd.DataFrame([])
    #     # for i in range(1, 100):
    #     #     df_append = df_append.append(df_signal)
    #     return df_signal

def retrieve_data():
    df_signal = DataFrame([])
    if ble_interface.connection:
        df_signal = ble_interface.read_gatt()
        print(df_signal)
    return df_signal