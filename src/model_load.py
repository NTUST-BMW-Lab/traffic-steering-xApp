import joblib
from mdclogpy import Logger
import tensorflow as tf

logger = Logger(name=__name__)


class ModelLoad(object):
    r""" Load the model

    Parameters:
    tfLite:bool
    """

    def __init__(self, tfLite = True):
        self.tfLite = tfLite
        self.load_model()
        self.load_scale()
    
    def load_model(self):
        try:
            if self.tfLite:
                self.tfLite = True
                self.model = tf.lite.Interpreter(model_path='model.tflite')
                self.model.allocate_tensors()
            else:
                self.tfLite = False
                self.model = tf.keras.models.load_model('model.h5')
        except FileNotFoundError:
            logger.error("Model Does not exsist")

    def load_scale(self):
        try:
            with open('src/scale', 'rb') as f:
                self.scale = joblib.load(f)
        except FileNotFoundError:
            logger.error("Scale file does not exsist")

    def predict(self, inputs):
        pred = None
        if self.tfLite:
            input_details = self.model.get_input_details()
            output_details = self.model.get_output_details()
            self.model.set_tensor(input_details[0]['index'], inputs)
            self.model.invoke()
            pred = self.model.get_tensor(output_details[0]['index'])
        else:
            pred = self.model.predict(inputs)
        pred = self.scale.inverse_transform(pred)
        return pred


class CAUSE(object):
    r""""Rule basd method to find degradation type of anomalous sample

    Attributes:
    normal:DataFrame
        Dataframe that contains only normal sample
    """

    def __init__(self):
        self.normal = None

    def cause(self, df, db):
        """ Filter normal data for a particular ue-id to compare with a given sample
            Compare with normal data to find and return degradaton type
        """
        sample = df.copy()
        sample.index = range(len(sample))
        for i in range(len(sample)):
            if sample.iloc[i]['Anomaly'] == 1:
                query = """select * from "{}" where {} = \'{}\' and time<now() and time>now()-20s""".format(db.meas, db.ue, sample.iloc[i][db.ue])
                normal = db.query(query)
                if normal:
                    normal = normal[db.meas][[db.thpt, db.rsrp, db.rsrq]]
                    deg = self.find(sample.loc[i, :], normal.max(), db)
                    if deg:
                        sample.loc[i, 'Degradation'] = deg
                        if 'Throughput' in deg and ('RSRP' in deg or 'RSRQ' in deg):
                            sample.loc[i, 'Anomaly'] = 2
                    else:
                        sample.loc[i, 'Anomaly'] = 0
        return sample[['Anomaly', 'Degradation']].values.tolist()

    def find(self, row, l, db):
        """ store if a particular parameter is below threshold and return """
        deg = []
        if row[db.thpt] < l[db.thpt]*0.5:
            deg.append('Throughput')
        if row[db.rsrp] < l[db.rsrp]-15:
            deg.append('RSRP')
        if row[db.rsrq] < l[db.rsrq]-10:
            deg.append('RSRQ')
        if len(deg) == 0:
            deg = False
        else:
            deg = ' '.join(deg)
        return deg
