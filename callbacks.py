import pandas as pd
import os
import numpy as np
from tensorflow.keras.callbacks import Callback
import time

class HistoryCallback(Callback):
    def __init__(self, settings, keys=[]):
        """Cosmos用のログのCallback
        
        Arguments:
            setting {dict} -- 設定値。output_dirが必須。ログはsettings['output_dir']/result.csvに記録
            keys {stringのlist} -- ログの項目のヘッダー。result.csvがあれば無視される。またKerasのon_epoch_endでも無視される
        """
        self.out_path = settings["output_dir"] + "/result.csv"
        if not os.path.exists(settings["output_dir"]):
            os.makedirs(settings["output_dir"])
        if os.path.exists(self.out_path):
            try:
                self.log_data = pd.read_csv(self.out_path)
                self.keys = np.setdiff1d(self.log_data.columns.values, ["epoch", "time"]).tolist()
            except:
                self.log_data = pd.DataFrame()
                self.keys = keys
        else:
            self.log_data = pd.DataFrame()
            self.keys = keys

    def on_epoch_end(self, epoch, logs):
        """Kerasのコールバックを使い自動的に記録
        
        Arguments:
            epoch {int} -- 現在のエポック
            logs {dict} -- KVSによる評価関数の値
        """

        row = {}
        row["epoch"] = [self.log_data.shape[0] + 1]
        row["time"] = [int(time.time())]  # Unix時間
        for k, v in logs.items():
            row[k] = [v]
        df = pd.DataFrame(row)
        self.log_data = pd.concat([self.log_data, df], axis=0, ignore_index=True)
        self.log_data.to_csv(self.out_path, index=False)
        
    def update(self, list_metrics):
        """カスタム訓練用のアップデート
        
        Arguments:
            list_metrics {list} -- 評価関数の値のリスト
        """
        if len(list_metrics) > len(self.keys):
            raise KeyError("キーに対して評価値が多すぎます")
        logs = {}
        for i in range(min(len(list_metrics), len(self.keys))):
            logs[self.keys[i]] = list_metrics[i]
        self.on_epoch_end(self.log_data.shape[0] + 1, logs)
        