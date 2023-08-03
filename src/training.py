import tensorflow as tf
from database import Database
from cleansing import Cleansing

class Training(object):
    """Training the data if the model doesn't exist
        
        Args:
            df (DataFrame): An datasets that want to be train to outcome the model
    """
    
    def __init__(self,df):
        """Initialize the Cleansing instance.
        
        Args:
            df (DataFrame): An datasets that want to be train to outcome the model
        """
        self.df = df

    def create_model_forecasting(self,time_steps=30,optimizer='adam',loss='mean_squared_error'):
        """Create the model summary with 3D-CNN-LSTM
        
        Args:
            time_steps (int): A lookback training from time_step before and predict time_step ahead.
            optimizers (String): An optimizer of the model. It effects to how fast the model is created (For Further Information what kind of opimizer, you can see the tensorflow websites)
            loss (String): A loss function. as machine learning or deep learning are fixed the model from loss, the loss function also determine how fast the model is created (For Further Information what kind of loss function, you can see the tensorflow websites)
        """
        model_3dcnn = tf.keras.Sequential([
            tf.keras.layers.Conv3D(filters=32, kernel_size=(3, 3, 3), activation='relu', input_shape=(time_steps, 7, 1, 1), padding='same'),
            tf.keras.layers.MaxPooling3D(pool_size=(2, 2, 2), strides=(1, 1, 1), padding='same'),
            tf.keras.layers.Conv3D(filters=64, kernel_size=(3, 3, 3), activation='relu', padding='same'),
            tf.keras.layers.MaxPooling3D(pool_size=(2, 2, 2), strides=(1, 1, 1), padding='same'),
            tf.keras.layers.Flatten()
        ])
        lstm_input_shape = model_3dcnn.output_shape[1:]
        lstm_model = tf.keras.Sequential([
            tf.keras.layers.Reshape((time_steps, -1)),
            tf.keras.layers.LSTM(256, activation='relu', input_shape=lstm_input_shape, return_sequences = True),
            tf.keras.layers.LSTM(128, activation='relu'),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(time_steps * 7, activation='linear'),
            tf.keras.layers.Reshape((time_steps, 7))
        ])
        combined_input = tf.keras.layers.Input(shape=(time_steps, 7, 1, 1))
        cnn_output = model_3dcnn(combined_input)
        lstm_output = lstm_model(cnn_output)
        self.combined_model = tf.keras.models.Model(inputs=combined_input, outputs=lstm_output)
        self.combined_model.compile(optimizer=optimizer, loss=loss, metrics=['accuracy'])

    def train(self,epochs=50,batch_size=32,val_split=0.2):
        """Train of the model that has been created from create_model_forecasting()
        
        Args:
            epochs (int): How many epochs train, it effets to how fast data will produce
            batch_size (int): A number of samples that will be used in a single iteration (forward and backward pass) of training in a machine learning algorithm, particularly in deep learning models like neural networks.
            val_split (float): A validation split in the context of training a machine learning or deep learning model. During the training process, it's common to split your available labeled data into three main subsets: the training set, the validation set, and the test set.
        """
        
        cleaner = Cleansing(self.df,10)
        cleaner.normalizer()
        input_train, output_train = cleaner.create_sequences()
        self.create_model_forecasting()
        self.combined_model.fit(input_train, output_train, epochs=epochs, batch_size=batch_size, validation_split=val_split)
    
    def model_saved(self):
        """Saved the model into .h5 (.tf) file"""
        
        self.combined_model.save(f"./src/model.h5")
    
    def model_saved_lite(self):
        """Saved the model into .tflite file"""
        
        converter = tf.lite.TFLiteConverter.from_keras_model(self.combined_model)
        tflite_model = converter.convert()
        with open('./src/model.tflite', 'wb') as f:
            f.write(tflite_model)
