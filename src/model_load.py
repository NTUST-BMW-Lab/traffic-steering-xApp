import joblib
from mdclogpy import Logger
import tensorflow as tf

logger = Logger(name=__name__)


class ModelLoad(object):
    r""" Load the model

    Parameters
    ----------
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