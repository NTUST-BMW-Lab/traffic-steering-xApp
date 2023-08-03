# Traffic Prediction xApp



## A. Directory Structure
```bash
Traffic-Prediction-xApp
|__ src # The folder of source code of xApp do
|   |__ cleansing.py # Make the data more trainable by cleansing it in scaler and create the sequences for training
|   |__ database.py # Connecting to the database (InfluxDB) 
|   |__ exceptions.py # Exception When The Code Not Execution Properly
|   |__ main.py # Main File To Execution the xApp
|   |__ model_load.py # Load the model that already exist
|   |__ training.py # Train the model if the model isn't already exist
|__ xapp-descriptor # The folder of description of the xApp in Kubernetes
|   |__ config.json # Configuration file for description of xApp
|   |__ schema.json # Control section of container in one node of kubernetes
|__ container-tag.yaml # Version Container
|__ Dockerfile # DockerFile for running the xApp in container image of xApp
|__ INFO.yaml # Information of the code
|__ LICENSE # License of the code
|__ local.rt # Set the message type that will be used as RMR seed
|__ rmr-version.yaml # Set the RMR version
|__ setup.py # Setup the xApp as Python Image and set library that necessary
|__ tox.ini # Description of xApp Package
```



## B. Requirements
### B.1 Python Library
- Python 3.x
- NumPy
- Pandas
- TensorFlow
- RICxAPPFrame
- JobLib
- MDCLogpy
- InfluxDB
- Scikit-Learn
### B.2 Image and Container
- KUBEV v1.16.0
- HELMV 3.5.4
- DOCKERV 20.10.21


## C. Running The xApp and Deploy it into local K8S
### Running in Docker
```bash
docker build -t tp-xapp:latest -f  Dockerfile .
docker run -i --net=host tp-xapp:latest
```
### xApp Deployment
```bash
docker build -t tp-xapp:latest -f  Dockerfile .
export CHART_REPO_URL=http://0.0.0.0:8090
dms_cli onboard ./xapp-descriptor/config.json ./xapp-descriptor/schema.json
dms_cli install tp-xapp 1.0.0 ricxapp
```


## D. Data Cleansing
Not all the data can be directly trained in any model of intelligence control. They should be cleaned first before utilize as reference data.
```python
class Cleansing(object):
    def __init__(self, df = None, lookback = 10):
      self.df = df
      self.lookback = lookback
```
Parameters:
1. `df` (DataFrame, required): The Data that performs the train.
2. `lookback` (Int, required) : The time step before of the train.
### Example Usage
```python
cleaner = Cleansing(df,10)
cleaner.normalizer()
input_train, output_train = cleaner.create_sequences()
```



## E. Model Load and Training
Load model and training are two different classes. The load model Class loads an existing model, but Training perfroms training to generate a model
### E.1 Model Load
Besides of load the model, This class also predict the data from the own methods
```python
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
```
Parameters:
1. `tfLite` (bool, required): The option where you stored the model, the lite or the original, True if using the lite model.

Other parameters:
2. `inputs` (DataFrame, required): The parameters use in predict the data using methods predits(DataFrame)
#### Example Usage
```python
md = ModelLoad(tfLite=False)
prediction = md.predict(DataFrame)
```
### E.2 Model Training
```python
class Training(object):
    r""" Training the model

    Parameters
    ----------
    df:DataFrame
    """
    def __init__(self,df):
        self.df = df
```
Parameters:
1. `df` (DataFrame, required): The Data that performs the train.
#### Models 3D-CNN LSTM
3D-CNN LSTM (Convolutional Neural Network Long Short-Term Memory) is a hybrid neural network architecture that combines the strengths of 3D Convolutional Neural Networks (3D-CNNs) and Long Short-Term Memory (LSTM) networks. This architecture is specifically designed for processing spatio-temporal data, such as video sequences or 3D time series data.
```python
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
combined_model = tf.keras.models.Model(inputs=combined_input, outputs=lstm_output)
combined_model.compile(optimizer=optimizer, loss=loss, metrics=['accuracy'])
```
The model utilize the 3D-CNN-LSTM because the data itself that from many base station and gather together in one data. The base station represent each matrix that could be visualize as big matrix in one data. Thus, to make matrix represents each base, it converts to 3D matrix. The best methods to predict is using the 3D-CNN. Afterthat, LSTM helps to predict future steps ahed of what base station output next.


## F. Database (InfluxDB)
Data that stored in database from UE fetch via InfluxDB.
```python
class Database(object):
    r"""
    Fetch the data from InfluxDB. InfluxDB has method get_field, get_measurement, get_start, get_stop, get_time, and get_value

    Parameters
    ----------
    url: String
    token: String
    org: String
    bucket: String
    """
    def __init__(self, url='', token='', org='', bucket='kpimon'):
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket
        self.client = None
        self.config()
```
Parameters:
1. `url` (String, required) : The url of database
2. `token` (String, required) : The token of influxDB
3. `org` (String, required) : The org that want to fetch
4. `bucket` (String, required) : The bucket that want to fetch

