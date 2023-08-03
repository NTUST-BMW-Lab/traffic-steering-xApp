import joblib
from mdclogpy import Logger
import tensorflow as tf

logger = Logger(name=__name__)


class ModelLoad(object):
    """Load the model if exist in ./src file directory
        
        Args:
            tfLite (bool): A choose of load data depends on what the model saved in the .tf or .tflite. True if save in .tflite and otherwise.
    """

    def __init__(self, tfLite = True):
        """Initialize the Cleansing instance.
        
        Args:
            tfLite (bool): A choose of load data depends on what the model saved in the .tf or .tflite. True if save in .tflite and otherwise.
        """
        self.tfLite = tfLite
        self.load_model()
        self.load_scale()
    
    def load_model(self):
        """Load the model either tfLite or tf depend on what model saved in ./src file directory"""
        
        try:
            if self.tfLite:
                self.tfLite = True
                self.model = tf.lite.Interpreter(model_path='./src/model.tflite')
                self.model.allocate_tensors()
            else:
                self.tfLite = False
                self.model = tf.keras.models.load_model('./src/model.h5')
        except FileNotFoundError:
            logger.error("Model Does not exsist")

    def load_scale(self):
        """Load the scale that has been store by normalized function"""
        
        try:
            with open('./src/scale', 'rb') as f:
                self.scale = joblib.load(f)
        except FileNotFoundError:
            logger.error("Scale file does not exsist")

    def predict(self, inputs):
        """Prediction function from dataframe arguments.

        Args:
            inputs (DataFrame): A data represent to predict in DataFrame from Pandas Python Library.
        """
        
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
