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