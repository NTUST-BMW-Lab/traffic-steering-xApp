#!/usr/bin/python3

import time
from mdclogpy import Logger
from influxdb_client import InfluxDBClient
from configparser import ConfigParser
from influxdb_client.rest import ApiException
import pandas as pd

logger = Logger(name=__name__)

class Database(object):
    """Fetch the data from InfluxDB. InfluxDB has method get_field, get_measurement, get_start, get_stop, get_time, and get_value
        
        Args:
            url (String): The url of the influxDB that you want to link it.
            token (String): The tokenize of influxDB.
            org (String): The destination org that you want to fetch
            bucket (String): The destination bucket that you want to fetch
    """
    def __init__(self, url='', token='', org='', bucket=''):
        """Initialize the Database instance.
        
        Args:
            url (String): The url of the influxDB that you want to link it.
            token (String): The tokenize of influxDB.
            org (String): The destination org that you want to fetch
            bucket (String): The destination bucket that you want to fetch
        """
        
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket
        self.client = None
        self.config()

    def connect(self):
        """Connect to the link database that has been declare"""
        
        self.config()
        if self.client is not None:
            self.client.close()
        try:
            self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
            logger.info("Connected to Influx Database")
            return True
        except ApiException as e:
            logger.error(f"Error connecting to InfluxDB server: {e}")
            time.sleep(30)
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            time.sleep(30)
    
    def disconnect(self):
        """Disconnect from the database"""
        
        if self.client is not None:
            self.client.close()

    def queries(self,params):
        """Initialize the Database instance.
        
        Args:
            params (String): The argument of parameters for fetch last data,.e.g. [|> range(start: -1m)]
        """

        try:
            column_names = ['DRB_UEThpUl', 'Viavi_Nb1_Rsrp', 'Viavi_Nb1_Rsrq', 'Viavi_Nb2_Rsrp', 'Viavi_Nb2_Rsrq', 'Viavi_UE_Rsrp', 'Viavi_UE_Rsrq']
            value_result = dict()
            for column in column_names:
                value_result[column] = []
            queriese = f'from(bucket: {self.bucket}) {params}'
            tables = self.client.query_api().query(queriese, org=self.org)
            if len(tables) > 0:
                for table in tables:
                    for record in table.records:
                        if record.get_measurement() == 'UeMetrics' and record.get_field() in column_names:
                            value_result[record.get_field()].append(record.get_value())
            return pd.DataFrame(value_result)
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return None

    def config(self):
        """Declare the data hasbeen store from .ini file and restore it in this function such as url,token,org, and bucket"""
        
        cfg = ConfigParser()
        cfg.read('./src/tf_config.ini')
        for section in cfg.sections():
            if section == 'InfluxDB':
                self.url = cfg.get(section, "url")
                self.token = cfg.get(section, "token")
                self.org = cfg.get(section, "org")
                self.bucket = cfg.get(section, "bucket")

# if __name__ == "__main__":
#     db = Database()
#     db.connect()
#     res = db.queries(params="|> range(start: -0.3s)")
#     db.disconnect()
