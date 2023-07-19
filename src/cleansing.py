import math
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Bidirectional
from sklearn.preprocessing import MinMaxScaler
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_squared_error
from google.colab import drive
import pandas as pd
import datetime
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import rfft, irfft

drive.mount('/content/drive')

df_ue = pd.read_csv('drive/MyDrive/NTUST BWM LAB/uedata.csv')
df_ue.reset_index(drop=True, inplace=True)
df_ue.drop(['table','_measurement','_start','_stop'], axis=1, inplace=True)
unique_field = df_ue['_field'].unique()
unique_timeseries = sorted(df_ue['_time'].unique())
column_listed = list(df_ue.columns)

for listed in range(5,11):
  df_ue.drop([column_listed[listed]], axis=1, inplace=True)

df_ue['_time'] = pd.to_datetime(df_ue['_time'])
df_ue.reset_index(drop=True, inplace=True)

field_idb = df_ue.groupby('_field')

dict_new_analytics = dict()

for i in range(len(unique_field)):
  dict_new_analytics[unique_field[i]] = list(field_idb.get_group(unique_field[i])["_value"])

df_new_analytics = pd.DataFrame(dict_new_analytics)

def drop_high_correlation_columns(df, threshold):
    corr_matrix = df.corr().abs()
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    columns_to_drop = [column for column in upper.columns if any(upper[column] > threshold)]
    df.drop(columns=columns_to_drop, inplace=True)
    return df

threshold = 0.95
df_new_analytics = df_new_analytics.drop(['DRB_UECqiDl','DRB_UECqiUl','DRB_UEThpUl','QosFlow_TotPdcpPduVolumeDl','RRU_PrbUsedDl','RRU_PrbUsedUl','TB_TotNbrDl','TB_TotNbrUl','Viavi_Geo_x','Viavi_Geo_y','Viavi_Geo_z','Viavi_Nb1_RsSinr','Viavi_Nb2_RsSinr','Viavi_QoS_5qi','Viavi_QoS_Gfbr','Viavi_QoS_Mfbr','Viavi_QoS_Priority','Viavi_QoS_Score','Viavi_QoS_TargetTput','Viavi_UE_RsSinr','Viavi_UE_anomalies','Viavi_UE_targetThroughputDl','Viavi_UE_targetThroughputUl'],axis=1)