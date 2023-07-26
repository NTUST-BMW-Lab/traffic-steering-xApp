# Traffic Prediction xAppp

## A. Directory Structure
```bash
Traffic-Prediction-xApp
|__ src # The source code of xApp do
|   |__ cleansing.py # Make the data more trainable by cleansing it in scaler and create the sequences for training
|   |__ database.py # Connecting to the database (InfluxDB) fro  
|   |__ exceptions.py
|   |__ main.py
|   |__ model_load.py
|   |__ training.py
|__ xapp-descriptor
|   |__ config.json
|__ container-tag.yaml
|__ Dockerfile
|__ INFO.yaml
|__ LICENSE
|__ local.rt
|__ rmr-version.yaml
|__ setup.py
|__ tox.ini
```


## B. Requirements
- Python 3.x
- NumPy
- Pandas
- TensorFlow
- RICxAPPFrame
- JobLib
- MDCLogpy
- InfluxDB
- Scikit-Learn
- Schedule

## C Data Cleansing

## D. Model Load and Training
Load model and training are two different classes. The load model Class loads an existing model, but Training perfroms training to generate a model
### D.1 Model Load
Besides of load the model, This class also predict the data from the own methods
```python
class ModelLoad(object):
    r""" Load the model

    Parameters:
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

### D.2 Model Training
```python
class Training(object):
    r""" Training the model

    Parameters:
    df:DataFrame
    """
    def __init__(self,df):
        self.df = df
```
other parameters
1. `df` (DataFrame, required): The Data that performs the train.

#### Models 3D-CNN LSTM
3D-CNN LSTM (Convolutional Neural Network Long Short-Term Memory) is a hybrid neural network architecture that combines the strengths of 3D Convolutional Neural Networks (3D-CNNs) and Long Short-Term Memory (LSTM) networks. This architecture is specifically designed for processing spatio-temporal data, such as video sequences or 3D time series data.

