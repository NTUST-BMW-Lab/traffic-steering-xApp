from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import numpy as np

class CLEANSING(object):
    def __init__(self, df):
      self.df = df

    def change_to_field(self):
        unique_field = self.df['_field'].unique()
        field_idb = self.df.groupby('_field')
        dict_new_analytics = dict()
        for i in range(len(unique_field)):
           dict_new_analytics[unique_field[i]] = list(field_idb.get_group(unique_field[i])["_value"])
        df_new_analytics = pd.DataFrame(dict_new_analytics)
        df_new_analytics = df_new_analytics.drop(['DRB_UECqiDl','DRB_UECqiUl','DRB_UEThpDl','QosFlow_TotPdcpPduVolumeDl','RRU_PrbUsedDl','RRU_PrbUsedUl','TB_TotNbrDl','TB_TotNbrUl','Viavi_Geo_x','Viavi_Geo_y','Viavi_Geo_z','Viavi_Nb1_RsSinr','Viavi_Nb2_RsSinr','Viavi_QoS_5qi','Viavi_QoS_Gfbr','Viavi_QoS_Mfbr','Viavi_QoS_Priority','Viavi_QoS_Score','Viavi_QoS_TargetTput','Viavi_UE_anomalies','Viavi_UE_targetThroughputDl','Viavi_UE_targetThroughputUl'],axis=1)
        return df_new_analytics

    def normalizer(self):
        column_df_analytics = list(self.df.columns)
        scaler = MinMaxScaler(feature_range=(0, 1))
        self.df[column_df_analytics] = scaler.fit_transform(self.df[column_df_analytics])

    def create_sequences(self, data, lookback):
        X, y = [] , []
        for i in range(len(data) - lookback):
            X.append(data[i:(i + lookback), :])
            y.append(data[i + lookback, :])
        return np.array(X), np.array(y)
    
    def split_data(self,x,length_split=0.8):
        split_index = int(length_split * len(x))
        return x[:split_index], x[split_index:]