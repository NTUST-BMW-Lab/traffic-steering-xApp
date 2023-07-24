import tensorflow as tf
from database import Database
from cleansing import Cleansing

'''
OUTPUT ON TRAINING AND SAVED IN SAVE
'''

class Training(object):
    def __init__(self,df):
        self.df = df

    def create_model_forecasting(self,time_steps=30,optimizer='adam',loss='mean_squared_error'):
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
            tf.keras.layers.LSTM(256, activation='relu', input_shape=lstm_input_shape),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(7, activation='linear')
        ])
        combined_input = tf.keras.layers.Input(shape=(time_steps, 7, 1, 1))
        cnn_output = model_3dcnn(combined_input)
        lstm_output = lstm_model(cnn_output)
        self.combined_model = tf.keras.models.Model(inputs=combined_input, outputs=lstm_output)
        self.combined_model.compile(optimizer=optimizer, loss=loss, metrics=['accuracy'])

    def train(self,epochs,batch_size,val_split):
        self.get_data_from_DB()
        cleaner = Cleansing(self.df)
        cleaner.normalizer()
        input_train, output_train = cleaner.create_sequences(self.df.values)
        self.create_model_forecasting()
        self.combined_model.fit(input_train, output_train, epochs=epochs, batch_size=batch_size, validation_split=val_split)
    
    def model_saved(self):
        self.combined_model.save(f"model.h5")
    
    def model_saved_lite(self):
        converter = tf.lite.TFLiteConverter.from_keras_model(self.combined_model)
        tflite_model = converter.convert()
        with open('model.tflite', 'wb') as f:
            f.write(tflite_model)