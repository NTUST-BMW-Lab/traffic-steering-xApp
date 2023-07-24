#!/usr/bin/python3

import time
from mdclogpy import Logger
from influxdb_client import InfluxDBClient
from configparser import ConfigParser
from influxdb_client.rest import ApiException
import pandas as pd

logger = Logger(name=__name__)

'''
get_field
get_measurement
get_start
get_stop
get_time
get_value
row
table
values
'''

class Database(object):
    def __init__(self, url='', token='', org='', bucket='kpimon'):
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket
        self.client = None
        self.config()

    def connect(self):
        try:
            self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
            logger.info("Conected to Influx Database")
            return True
        except ApiException as e:
            logger.error(f"Error connecting to InfluxDB server: {e}")
            time.sleep(30)
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            time.sleep(30)
    
    def disconnect(self):
        if self.client is not None:
            self.client.close()

    def queries(self,param):
        '''
        Param 
        Example |> range(start: -1m)
        '''
        column_names = ['DRB_UEThpUl', 'Viavi_Nb1_Rsrp', 'Viavi_Nb1_Rsrq', 'Viavi_Nb2_Rsrp', 'Viavi_Nb2_Rsrq', 'Viavi_UE_Rsrp', 'Viavi_UE_Rsrq']
        value_result = dict()
        for column in column_names:
            value_result[column] = []
        query = f'from(bucket: "{self.bucket}") {param}'
        tables = self.client.query_api().query(query, org=self.org)
        for table in tables:
            for record in table.records:
                if record.get_measurement() == 'UeMetrics' and record.get_field() in column_names:
                    value_result[record.get_field()].append(record.get_value())
        return pd.DataFrame(value_result)

    def config(self):
        cfg = ConfigParser()
        cfg.read('tf_config.ini')
        for section in cfg.sections():
            if section == 'InfluxDB':
                self.url = cfg.get(section, "url")
                self.token = cfg.get(section, "token")
                self.org = cfg.get(section, "org")
                self.bucket = cfg.get(section, "bucket")

if __name__ == "__main__":
    db = Database()
    db.connect()
    res = db.queries("|> range(start: -1s)")
    print(res)
    db.disconnect()