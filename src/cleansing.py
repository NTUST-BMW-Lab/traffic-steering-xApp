from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import numpy as np
import joblib

class Cleansing(object):
    r""" 
    Clean the data
    -------------

    Parameters:
        df: DataFrame (default = None)
        lookback: int (default = 10)
    """
    def __init__(self, df = None, lookback = 10):
      
      self.df = df
      self.lookback = lookback

    def change_to_field(self):
        unique_field = self.df['_field'].unique()
        field_idb = self.df.groupby('_field')
        dict_new_analytics = dict()
        for i in range(len(unique_field)):
           dict_new_analytics[unique_field[i]] = list(field_idb.get_group(unique_field[i])["_value"])
        df_new_analytics = pd.DataFrame(dict_new_analytics)
        df_new_analytics = df_new_analytics.drop(['DRB_UECqiDl','DRB_UECqiUl','DRB_UEThpDl','QosFlow_TotPdcpPduVolumeDl','RRU_PrbUsedDl','RRU_PrbUsedUl','TB_TotNbrDl','TB_TotNbrUl','Viavi_Geo_x','Viavi_Geo_y','Viavi_Geo_z','Viavi_Nb1_RsSinr','Viavi_Nb2_RsSinr','Viavi_QoS_5qi','Viavi_QoS_Gfbr','Viavi_QoS_Mfbr','Viavi_QoS_Priority','Viavi_QoS_Score','Viavi_QoS_TargetTput','Viavi_UE_anomalies','Viavi_UE_targetThroughputDl','Viavi_UE_targetThroughputUl'],axis=1)
        df_new_analytics['DRB_UEThpUl'] = df_new_analytics['DRB_UEThpUl'].apply(lambda x: x*1024)
        return df_new_analytics

    def normalizer(self):
        column_df_analytics = list(self.df.columns)
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaler_saved = scaler.fit(self.df[column_df_analytics])
        joblib.dump(scaler_saved, 'src/scale')
        self.df[column_df_analytics] = scaler.transform(self.df[column_df_analytics])

    def create_sequences(self):
        samples = len(self.df.values) - self.lookback + 1
        input_data = np.zeros((samples, self.lookback, 7, 1, 1))
        output_data = np.zeros((samples, 7))
        for i in range(samples):
            input_data[i] = self.df.values[i:i+self.lookback].reshape((self.lookback, 7, 1, 1))
            output_data[i] = self.df.values[i+self.lookback-1]
        return input_data,output_data