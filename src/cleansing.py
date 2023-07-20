import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
from google.colab import drive
import pandas as pd
import numpy as np
from sklearn.preprocessing import Normalizer

drive.mount('/content/drive')

class CLEANSING(object):
    def __init__(self, df):
      self.df = df

    def change_to_field(self):
        field_idb = self.df.groupby('_field')
        dict_new_analytics = dict()
        for i in range(len(unique_field)):
           dict_new_analytics[unique_field[i]] = list(field_idb.get_group(unique_field[i])["_value"])
        df_new_analytics = pd.DataFrame(dict_new_analytics)
        df_new_analytics = df_new_analytics.drop(['DRB_UECqiDl','DRB_UECqiUl','DRB_UEThpDl','QosFlow_TotPdcpPduVolumeDl','RRU_PrbUsedDl','RRU_PrbUsedUl','TB_TotNbrDl','TB_TotNbrUl','Viavi_Geo_x','Viavi_Geo_y','Viavi_Geo_z','Viavi_Nb1_RsSinr','Viavi_Nb2_RsSinr','Viavi_QoS_5qi','Viavi_QoS_Gfbr','Viavi_QoS_Mfbr','Viavi_QoS_Priority','Viavi_QoS_Score','Viavi_QoS_TargetTput','Viavi_UE_anomalies','Viavi_UE_targetThroughputDl','Viavi_UE_targetThroughputUl'],axis=1)
        return df_new_analytics

    def normalizer(self):
        self.df = self.df.dropna(axis=0)

    def create_sequences(self, data, lookback):
        X, y = [] , []
        for i in range(len(data) - lookback):
            X.append(data[i:(i + lookback), :])
            y.append(data[i + lookback, :])
        return np.array(X), np.array(y)

df_ue = pd.read_csv('drive/MyDrive/NTUST BWM LAB/uedata.csv')
df_ue.reset_index(drop=True, inplace=True)
df_ue.drop(['table','_measurement','_start','_stop'], axis=1, inplace=True)
unique_field = df_ue['_field'].unique()
unique_timeseries = sorted(df_ue['_time'].unique())
column_listed = list(df_ue.columns)

for listed in range(5,11):
  df_ue.drop([column_listed[listed]], axis=1, inplace=True)


df_ue['_time'] = pd.to_datetime(df_ue['_time'])

# df_ue.sort_values(by='_time', inplace=True)
df_ue.reset_index(drop=True, inplace=True)

field_idb = df_ue.groupby('_field')

dict_new_analytics = dict()

for i in range(len(unique_field)):
  dict_new_analytics[unique_field[i]] = list(field_idb.get_group(unique_field[i])["_value"])

df_new_analytics = pd.DataFrame(dict_new_analytics)

df_new_analytics = df_new_analytics.drop(['DRB_UECqiDl','DRB_UECqiUl','DRB_UEThpDl','QosFlow_TotPdcpPduVolumeDl','RRU_PrbUsedDl','RRU_PrbUsedUl','TB_TotNbrDl','TB_TotNbrUl','Viavi_Geo_x','Viavi_Geo_y','Viavi_Geo_z','Viavi_Nb1_RsSinr','Viavi_Nb2_RsSinr','Viavi_QoS_5qi','Viavi_QoS_Gfbr','Viavi_QoS_Mfbr','Viavi_QoS_Priority','Viavi_QoS_Score','Viavi_QoS_TargetTput','Viavi_UE_anomalies','Viavi_UE_targetThroughputDl','Viavi_UE_targetThroughputUl'],axis=1)

new_data = []
MinMaxs = {'min':[],'max':[]}
column_df_analytics = list(df_new_analytics.columns)
scaler = MinMaxScaler(feature_range=(-1, 1))
df_new_analytics[column_df_analytics] = scaler.fit_transform(df_new_analytics[column_df_analytics])
for i in range(len(column_df_analytics)):
  MinMaxs['max'].append(np.max(df_new_analytics[column_df_analytics[i]]))
  MinMaxs['min'].append(np.min(df_new_analytics[column_df_analytics[i]]))

sequence_length = 10
X, y = create_sequences(df_new_analytics.values, sequence_length)

split_index = int(0.8 * len(X))
X_train, X_test = X[:split_index], X[split_index:]
y_train, y_test = y[:split_index], y[split_index:]

model1 = Sequential()
model1.add(LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
model1.add(LSTM(50, return_sequences=True))
model1.add(LSTM(50, return_sequences=True))
model1.add(LSTM(50, return_sequences=False))
model1.add(Dense(7, activation='tanh'))

model1.compile(optimizer='adam', loss='mse', metrics=['accuracy'])
history = model1.fit(X_train, y_train, epochs=50, batch_size=16, verbose=1)

trainPredict = model1.predict(X_train)

class CleansingData():
   def __init__(self) -> None:
      pass
   
   def dropColumn(self):
      pass