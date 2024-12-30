<h1 style="text-align:center;">
Convert a Python Machine Learning Model to Arduino Code (C++)
</h1>

# Introduction

### Motivation

<b>What ?</b> 
<br>
This project demonstrates the conversion of Python machine learning (ML) models to Arduino C++ code. 
<br>
We will use some ML models purely as examples; the goal is not to find the best model or achieve minimal error. 
<br> 
    <b>Why ?</b> 
<br>
In certain applications, such as embedded systems, small microcontrollers with limited memory and computing resources are used. The idea is to train a machine learning model in a Python environment and then convert the trained model to C++ for deployment on a microcontroller. 
<br>
In this project, we will use the Arduino Uno as an example, but the approach can be applied to other microcontrollers as well. 
<br>
<b>How ?</b> 
<br> 
Follow the step-by-step guide below, or go directly to the PyPi package <a href="https://pypi.org/search/?q=mltoarduino">mltoarduino</a>
<br><br>
<img src = "https://bouz1.github.io/fils/MLModelToArduinoCpp/illustration2.png">   

### Hardware

In this project, the Arduino Uno was used, but you can use other boards like Arduino Nano or Micro, Miga 2560, ESP32... <br> 
below a comparaison of some Arduino boards: 

| Feature                | Arduino Uno        | Arduino Nano       | Arduino Micro      | Arduino Mega 2560   | ESP32                |
|------------------------|--------------------|--------------------|--------------------|----------------------|----------------------|
| **Microcontroller**    | ATmega328P        | ATmega328P         | ATmega32U4         | ATmega2560           | Tensilica Xtensa LX6 |
| **Operating Voltage**  | 5V                | 5V                 | 5V                 | 5V                   | 3.3V                 |
| **Input Voltage**      | 7-12V             | 7-12V              | 7-12V              | 7-12V                | 5V via USB or 7-12V  |
| **Digital I/O Pins**   | 14 (6 PWM)        | 14 (6 PWM)         | 20 (7 PWM)         | 54 (15 PWM)          | 34                   |
| **Analog Input Pins**  | 6                 | 8                  | 12                 | 16                   | 18                   |
| **Flash Memory**       | 32 KB             | 32 KB              | 32 KB              | 256 KB               | Up to 16 MB          |
| **SRAM**               | 2 KB              | 2 KB               | 2.5 KB             | 8 KB                 | 520 KB               |
| **EEPROM**             | 1 KB              | 1 KB               | 1 KB               | 4 KB                 | None                 |
| **Clock Speed**        | 16 MHz            | 16 MHz             | 16 MHz             | 16 MHz               | 240 MHz (dual-core)  |
| **Connectivity**       | UART, I2C, SPI    | UART, I2C, SPI     | UART, I2C, SPI     | UART, I2C, SPI       | Wi-Fi, Bluetooth     |
| **USB Interface**      | USB-B             | Mini USB           | Micro USB          | USB-B                | Micro USB            |
| **Dimensions**         | 68.6 x 53.4 mm    | 45 x 18 mm         | 48 x 18 mm         | 101.52 x 53.3 mm     | 51 x 25.5 mm         |
| **Power Consumption**  | ~50 mA            | ~50 mA             | ~50 mA             | ~70 mA               | Varies (~80-240 mA)  |
| **Special Features**   | Simple and robust | Compact            | USB HID support    | High I/O count       | Wi-Fi and BLE        |
| **Price Range**        | Low               | Low                | Medium             | Medium               | Medium-High          |

# How to use the package


```python
# Install the package 
!pip install mltoarduino
```


```python
# Import all functions 
from mltoarduino import *
```

### Load an example data


```python
FileName="..\data\processed\df_price_4inputs.csv"
dfnew= pd.read_csv(FileName).astype("float32")
print("Df columns: ", list(dfnew.columns))
X= dfnew.iloc[:,:4].values
y= dfnew.iloc[:,4].values
# Split into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
```

    Df columns:  ['Gearbox_auto', 'HorseP', 'Euro_stand', 'km', 'price']
    

### Example of Linear Regression model


```python
# Load the model
LR_model = joblib.load(r'../models/LinearReg/LR_model.pkl')
```


```python
# Sub inputs/outpusts to test the arduino model: 10 samples
sub_X=X_train[:10]
sub_y=LR_model.predict(sub_X)
```


```python
# Convert the model to arduino C++
arduino_code= LinearRegToC (LR_model, sub_X, sub_y)
```


```python
print("100 first charaters of arduino code \n",arduino_code[:100])
```

    100 first charaters of arduino code 
     
    
    const int Nv = 10;
    const int dimX = 4;
    
    /////// Xy ////// 
    const float X [] PROGMEM  = {0.0, 116.0
    

You can use a code like below to save the arduino code.ino 
To avoid error in arduino environnement, if your file name is Example.ino
this file must be stored in the same folder name "Example/Example.ino"


```python
ino_file="ArduinoCode/LinearReg.ino" # Path of the file
ino_file=ino_file.replace(".ino" ,"")
current_directory = os.getcwd()
new_directory_path = os.path.join(current_directory, ino_file)
try:
    os.makedirs(new_directory_path)
except: pass

path=ino_file+"/"+ino_file.split("/")[-1]+".ino"
with open(path,'w+') as f:
    f.write(arduino_code)
    
    print(path, "saved")
```

<b>The arduino memory usnig</b>
<div style="background-color:black; color:white; padding-left:10px;">
Sketch uses 3906 bytes (12%) of program storage space. Maximum is 30720 bytes.
Global variables use 252 bytes (12%) of dynamic memory, leaving 1796 bytes for local variables. Maximum is 2048 bytes.
</div>


```python
# The arduino serial print result 
serialPrint="""
Cal_Ardui,Expected,Delta_time(us)
19074.86,19074.861328,68
22590.43,22590.433593,76
18458.25,18458.253906,80
20624.41,20624.408203,76
20219.45,20219.445312,76
29240.26,29240.261718,80
32525.00,32525.000000,84
27160.86,27160.859375,80
25408.60,25408.605468,80
26429.56,26429.554687,88
====The End====="""
```


```python
# Convert the serial result to DF 
data = serialPrint.split("\n")[1:-1]
data=[x.split(",") for x in data]
DF_serial= pd.DataFrame( data[1:], columns= data[0]).astype("float32")
DF_serial
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Cal_Ardui</th>
      <th>Expected</th>
      <th>Delta_time(us)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>19074.859375</td>
      <td>19074.861328</td>
      <td>68.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>22590.429688</td>
      <td>22590.433594</td>
      <td>76.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>18458.250000</td>
      <td>18458.253906</td>
      <td>80.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>20624.410156</td>
      <td>20624.408203</td>
      <td>76.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>20219.449219</td>
      <td>20219.445312</td>
      <td>76.0</td>
    </tr>
    <tr>
      <th>5</th>
      <td>29240.259766</td>
      <td>29240.261719</td>
      <td>80.0</td>
    </tr>
    <tr>
      <th>6</th>
      <td>32525.000000</td>
      <td>32525.000000</td>
      <td>84.0</td>
    </tr>
    <tr>
      <th>7</th>
      <td>27160.859375</td>
      <td>27160.859375</td>
      <td>80.0</td>
    </tr>
    <tr>
      <th>8</th>
      <td>25408.599609</td>
      <td>25408.605469</td>
      <td>80.0</td>
    </tr>
    <tr>
      <th>9</th>
      <td>26429.560547</td>
      <td>26429.554688</td>
      <td>88.0</td>
    </tr>
  </tbody>
</table>
</div>




```python
print("The AVG prediction time of one input is", 
      (DF_serial['Delta_time(us)'].mean()/1000).round(2), 
      "ms"
     ) 
```

    The AVG prediction time of one input is 0.08 ms
    


```python
# Ploting 
DF_serial.plot.scatter(x='Expected', y='Cal_Ardui',  marker='o', label="Arduino calculation")
xx=[DF_serial['Expected'].min(), DF_serial['Expected'].max()]
plt.plot(xx,xx, c='r', label="equal")
plt.legend()
plt.xlabel("Tenforflow model prediction")
plt.ylabel("Arduino model prediction")
plt.grid()
plt.show()
```


    
![png](https://bouz1.github.io/fils/MLModelToArduinoCpp/READMEFILS/README1/imgs/output_23_0.png)
    



```python
# The arduino and python model have the same result.
```

# Other models

You can use the same logic to convert other models to ARDUINO C++

| Function Name                   | Model Description                       |
|----------------------------------|-----------------------------------------|
| `convert_DecTree_To_C`           | Decision Tree Regression Model          |
| `convert_RandForest_To_C`        | Random Forest Regression Model          |
| `XGBOOST_to_CPP`                 | XGBoost Regression Model                |
| `tf_model_to_arduino_code`       | DNN TensorFlow Model                    |

For more information you can see the home page <br>
https://bouz1.github.io/fils/MLModelToArduinoCpp/MLModelToArduinoCpp.html
<br>
Or the github repository <br>
https://github.com/bouz1/ML-Model-To-Arduino-Cpp
