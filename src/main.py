import json
import os
import time
import pandas as pd
import schedule
from ricxappframe.xapp_frame import Xapp
from ricxappframe.xapp_sdl import SDLWrapper
from mdclogpy import Logger
from training import Training
from database import Database
from model_load import ModelLoad

db = None
df = None
sdl = SDLWrapper(use_fake_sdl=True)

logger = Logger(name=__name__)


def entry(self):
    connectdb()
    train_model()
    load_model()
    schedule.every(0.5).seconds.do(predict, self)
    while True:
        schedule.run_pending()


def load_model():
    global md
    md = ModelLoad()

def train_model():
    if not os.path.isfile('src/model.h5') or not os.path.isfile('src/model.5'):
        mt = Training(db)
        mt.train()
        mt.model_saved()

def predict(self):
    db.read_data()
    val = None
    if db.data is not None:
        if set(md.num).issubset(db.data.columns):
            db.data = db.data.dropna(axis=0)
        else:
            logger.warning("Parameters does not match with of training data")
    else:
        logger.warning("No data in last 1 second")
        time.sleep(1)
    if (val is not None) and (len(val) > 2):
        msg_to_xapp(self, val)

def msg_to_xapp(self, val):
    # send message from ad to ts
    logger.debug("Sending Anomalous UE to TS")
    success = self.rmr_send(val, 30003)
    if success:
        logger.info(" Message to TS: message sent Successfully")
    # rmr receive to get the acknowledgement message from the traffic steering.
    for (summary, sbuf) in self.rmr_get_messages():
        logger.info("Received acknowldgement from TS (TS_ANOMALY_ACK): {}".format(summary))
        self.rmr_free(sbuf)


def connectdb(thread=False):
    global db, df
    db = Database()
    success = False
    while not success:
        success = db.connect()
        db = Database()
        db.connect()
        df = db.queries("|> range(start: -1s)")


def start(thread=False):
    # Initiates xapp api and runs the entry() using xapp.run()
    xapp = Xapp(entrypoint=entry, rmr_port=4560, use_fake_sdl=False)
    xapp.logger.debug("Traffic Prediction xApp starting")
    xapp.run()
