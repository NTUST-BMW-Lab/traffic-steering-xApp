import json
import os
import time
import pandas as pd
import schedule
from mdclogpy import Logger
from training import Training
from database import Database
from model_load import ModelLoad
from ricxappframe.xapp_sdl import SDLWrapper
from ricxappframe.xapp_frame import Xapp

db = None
df = None
sdl = SDLWrapper(use_fake_sdl=True)

logger = Logger(name=__name__)


def entry(self):
    """The entry file of running the xApp. This is the xApp general function will run. This function run every 1 second to predict and send it."""
    
    connectdb()
    train_model()
    load_model()
    schedule.every(1).seconds.do(predict, self)
    while True:
        schedule.run_pending()


def load_model():
    """The model will be load if there model in ./src"""
    
    global md
    logger.info("Load the Model")
    md = ModelLoad(tfLite=False)

def train_model():
    """The model that will be trained while the model doesn't exist in ./src file"""
    
    if not os.path.exists(os.getcwd()+'/src/model.h5') and not os.path.exists(os.getcwd()+'/src/model.tflite'):
        logger.info("Start Training The Model")
        df = db.queries("|> range(start: -5h)")
        if len(df) == 0:
            logger.info("No Data in Database")
        else:
            mt = Training(df)
            mt.train()
            mt.model_saved()

def predict(self):
    """Prediction function from fetching last 1 second data and decode the prediction into JSON for sending it to network slicing xApp"""
    
    column_names = ['DRB_UEThpUl', 'Viavi_Nb1_Rsrp', 'Viavi_Nb1_Rsrq', 'Viavi_Nb2_Rsrp', 'Viavi_Nb2_Rsrq', 'Viavi_UE_Rsrp', 'Viavi_UE_Rsrq']
    df = db.queries("|> range(start: -1s)")
    val = None
    if len(df) > 0 and df is not None:
        val = md.predict(df)
        val = val[0]
        result_send = dict()
        for column in range(len(column_names)):
            result_send[column_names[column]] = val[:,column]
        result = json.loads(result_send.to_json(orient='records'))
        val = json.dumps(result).encode()
    else:
        logger.warning("No data in last 1 second")
        time.sleep(1)
    if (val is not None) and (len(val) > 0):
        msg_to_xapp(self, val)

def msg_to_xapp(self, val):
    """Sending the database to Slicing Network xApp as 80911 message type in 30 data prediction ahead"""
    
    logger.debug("Sending to Slicing Network xApp")
    success = self.rmr_send(val, 80901)
    if success:
        logger.info("Message to Slicing Network xApp: message sent Successfully")
    for (summary, sbuf) in self.rmr_get_messages():
        logger.info("Received acknowldgement from SLICING NETWORK xAPP: {}".format(summary))
        self.rmr_free(sbuf)


def connectdb(thread=False):
    """Connection to the database"""
    
    global db, df
    db = Database()
    success = False
    while not success:
        success = db.connect()


def start(thread=False):
    """Starting of xApp. xApp will execute this function. This Function initiates xApp API and runs the entry() using xapp.run()"""
    
    xapp = Xapp(entrypoint=entry, rmr_port=4560, use_fake_sdl=False)
    xapp.logger.debug("Traffic Prediction xApp starting")
    xapp.run()
