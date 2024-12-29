### Libraries
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import mean_absolute_error
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor

import xgboost as xgb

import tensorflow as tf

import matplotlib.pyplot as plt
import seaborn as sns

# save models
import joblib
import pickle

import os
import re
import json

### Utils : for all models

def array_to_arduino(x):
    """
    Helper function to convert a Python list or NumPy array to Arduino array format 
    for use in the generated Arduino code. 
    It converts the input into a string format where square brackets [] are replaced 
    with curly braces {}.

    Input:
    - x: List or array to be converted

    Output:
    - Formatted string that can be used in Arduino code
    """
    x = str(x.tolist())  # Convert array to list and then string
    x = x.replace('[', '{')  # Replace square brackets with curly braces
    x = x.replace(']', '}')  # Replace closing square bracket with closing curly brace
    return x

### Linear Regression
def LinearRegToC (model, X, y):
    """Convert a Linear regression model (sklearn) to C++ (Arduino)
    Model : trained LR model 
    X,y : input outputs to test the arduino code
    """
    codeInit="""

const int Nv = NvReplace;
const int dimX = dimXReplace;

/////// Xy ////// 
const float X [] PROGMEM  = Xreplace;

const float y[] PROGMEM  = yreplace;




////////////////// Model
const float coef[] PROGMEM = coefreplace; 
const float Bias = Biasreplace; 
float LinearReg ( float X[] ) {
float Out=Bias;
for(int j = 0; j<dimX;j++){
    Out+=X[j]*pgm_read_float_near(&coef[j]);
}

return Out;
}




void setup() {
    Serial.begin(115200);
}

void loop() {
unsigned long timestart;
unsigned long timeend;
float Xi[dimX];
float yc;


Serial.println("Cal_Ardui,Expected,Delta_time(us)");
for (int l=0;l<Nv;l++){
for(int j = 0; j<dimX;j++){
    Xi[j]=pgm_read_float_near(&X[l*dimX+j]);
}
timestart=micros();
yc=LinearReg(Xi);
timeend=micros();
Serial.print(yc);
Serial.print(",");
Serial.print(pgm_read_float_near(&y[l]),6);
Serial.print(",");
Serial.println(timeend-timestart);
}
Serial.println("====The End=====");
while(1);
}
"""    
    
    Nv, dimX= X.shape
    Nv, dimX= str(Nv), str(dimX)
    Xs=array_to_arduino(X.flatten())
    ys=array_to_arduino(y)
    coef = array_to_arduino(model.coef_)
    bias = str(model.intercept_)



    codeInit= codeInit.replace("NvReplace",Nv)
    codeInit= codeInit.replace("dimXReplace",dimX)
    codeInit= codeInit.replace("Xreplace",Xs)
    codeInit= codeInit.replace("yreplace",ys)
    codeInit= codeInit.replace("coefreplace",coef)
    codeInit= codeInit.replace("Biasreplace", bias)

    return codeInit




### Decision tree Regressor
def get_cpp_code_from_tree(tree, feature_names):
    """
    Convert a decision tree to if/else code C++
    """
    left      = tree.tree_.children_left
    right     = tree.tree_.children_right
    threshold = tree.tree_.threshold
    features  = [feature_names[i] for i in tree.tree_.feature]
    value = tree.tree_.value 
    code = ""
    def recurse(left, right, threshold, features, node):
            nonlocal code 
            if (threshold[node] != -2):
                    code+="if ( " + features[node] + " <= " + str(threshold[node]) + " ) {\n"
                    if left[node] != -1:
                            recurse (left, right, threshold, features,left[node])
                    code+="} else {\n"
                    if right[node] != -1:
                            recurse (left, right, threshold, features,right[node])
                    code+="}\n"
            else:
                    code+="return " + str(value[node]).replace("[","").replace("]","")+";\n"

    recurse(left, right, threshold, features, 0)
    return code

def convert_DecTree_To_C(model, X,y):
    codeInit="""

const int Nv = NvReplace;
const int dimX = dimXReplace;

/////// Xy ////// 
const float X [] PROGMEM  = Xreplace;

const float y[] PROGMEM  = yreplace;



////////////////// TREE
float DecisionTreeReg ( float X[] ) {
IF_ELSE_CONDITION_replace
}




void setup() {
    Serial.begin(115200);
}

void loop() {
unsigned long timestart;
unsigned long timeend;
float Xi[dimX];
float yc;


Serial.println("Cal_Ardui,Expected,Delta_time(us)");
for (int l=0;l<Nv;l++){
for(int j = 0; j<dimX;j++){
    Xi[j]=pgm_read_float_near(&X[l*dimX+j]);
}
timestart=micros();
yc=DecisionTreeReg(Xi);
timeend=micros();
Serial.print(yc);
Serial.print(",");
Serial.print(pgm_read_float_near(&y[l]),6);
Serial.print(",");
Serial.println(timeend-timestart);
}
Serial.println("====The End=====");
while(1);
}
"""

    Nv, dimX= X.shape
    Nv, dimX= str(Nv), str(dimX)
    Xs=array_to_arduino(X.flatten())
    ys=array_to_arduino(y)

    features = ["X["+str(i)+"]" for i in range(X.shape[1])]
    ifelsecode = get_cpp_code_from_tree(model, features)

    codeInit= codeInit.replace("NvReplace",Nv)
    codeInit= codeInit.replace("dimXReplace",dimX)
    codeInit= codeInit.replace("Xreplace",Xs)
    codeInit= codeInit.replace("yreplace",ys)
    codeInit= codeInit.replace("IF_ELSE_CONDITION_replace",ifelsecode)

    return codeInit



### Random forest regressor

def convert_RandForest_To_C(model, X,y):
    codeInit="""

const int Nv = NvReplace;
const int dimX = dimXReplace;

/////// Xy ////// 
const float X [] PROGMEM  = Xreplace;

const float y[] PROGMEM  = yreplace;



////////////////// TREES

TREES_replace 


////////////////// RANDOM FOREST 

RF_replace



void setup() {
Serial.begin(115200);
}

void loop() {
unsigned long timestart;
unsigned long timeend;
float Xi[dimX];
float yc;


Serial.println("Cal_Ardui,Expected,Delta_time(us)");
for (int l=0;l<Nv;l++){
for(int j = 0; j<dimX;j++){
Xi[j]=pgm_read_float_near(&X[l*dimX+j]);
}
timestart=micros();
yc=RandForestReg(Xi);
timeend=micros();
Serial.print(yc);
Serial.print(",");
Serial.print(pgm_read_float_near(&y[l]),6);
Serial.print(",");
Serial.println(timeend-timestart);
}
Serial.println("====The End=====");
while(1);
}
"""
    code_trees=""
    code_randForest="\n\n\nfloat RandForestReg ( float X[] ) {\nfloat out=0;\n"
    features = ["X["+str(i)+"]" for i in range(X.shape[1])]
    trees = model.estimators_
    for i, tree in enumerate(trees):
        code_tree=get_cpp_code_from_tree(tree,  features )
        code_tree="\n\n\nfloat Tree"+str(i)+" ( float X[] ) {\n"+code_tree+"\n}\n"
        code_trees+=code_tree

        code_randForest+="out+=Tree"+str(i)+" (X);\n";

    code_randForest+="out=out/"+str(model.n_estimators)+";\nreturn out;\n}\n"




    Nv, dimX= X.shape
    Nv, dimX= str(Nv), str(dimX)
    Xs=array_to_arduino(X.flatten())
    ys=array_to_arduino(y)

  

    codeInit= codeInit.replace("NvReplace",Nv)
    codeInit= codeInit.replace("dimXReplace",dimX)
    codeInit= codeInit.replace("Xreplace",Xs)
    codeInit= codeInit.replace("yreplace",ys)

    codeInit= codeInit.replace("TREES_replace",code_trees)
    codeInit= codeInit.replace("RF_replace",code_randForest)


    return codeInit


### XGBoost

# Function: TreesCode
# Description:
# This function generates C++ code representing the decision trees of an XGBoost model.
# It parses the model's JSON representation and recursively converts each tree into a C++ function.
def TreesCode(model):
    """
    Generates C++ code for each decision tree in an XGBoost model.

    The function extracts the tree structure in JSON format from the model and recursively
    traverses each tree to generate a corresponding C++ function. Each function represents
    the decision logic of a single tree, taking an input array `X` and returning the output.

    Args:
        model: The trained XGBoost model containing the decision trees.

    Returns:
        str: A string containing the complete C++ code for all trees in the model.
    """

    # Extract the JSON representation of the tree
    booster = model.get_booster()
    trees = booster.get_dump(dump_format="json")
    cpp_code = ""

    def recurse(node, depth=0):
        """
        Recursive helper function to traverse a tree node and generate corresponding C++ code.
        - If the node is a leaf, it appends a return statement with the leaf value.
        - Otherwise, it generates a conditional statement based on the split condition.

        :param node: Dictionary representation of a tree node.
        :param depth: Current depth of the node for indentation purposes.
        """
        nonlocal cpp_code
        indent = "    " * depth

        # Leaf node
        if "leaf" in node:
            cpp_code += f"{indent}return {node['leaf']};\n"
            return

        split_condition = node['split_condition']
        INDEX_INP= int(node['split'][1:])
        cpp_code += f"{indent}if (X[{INDEX_INP}] < {split_condition}) {{\n"
        recurse(node['children'][0], depth + 1)
        cpp_code += f"{indent}}} else {{\n"
        recurse(node['children'][1], depth + 1)
        cpp_code += f"{indent}}}\n"

    # Generate code for each tree
    for tree_index, tree_json in enumerate(trees):
        cpp_code += f"\n////////////////// TREE {tree_index}\n"
        cpp_code += f"float tree{tree_index}(float X[]) {{\n"
        tree_dict = json.loads(tree_json)
        recurse(tree_dict)
        cpp_code += "}\n\n"

    return cpp_code



# Function: code_trees
# Description:
# Generates the cumulative summation of the predictions from all trees, formatted as C++ code.
# The summation depends on the learning rate and number of trees.
def code_trees(N, learning_rate): 
    XGBOOST_CODE= ""
    for index in range(N):
        if learning_rate  == "1": 
            XGBOOST_CODE+= f"out+= tree{index}(X);\n"
        else: 
            XGBOOST_CODE+= f"out+= learning_rate*tree{index}(X);\n"
    return XGBOOST_CODE




# Function: XGBOOST_to_CPP
# Description:
# Converts an XGBoost model to a complete C++ implementation for predictions.
# This includes tree code, model initialization, and a prediction function.
def XGBOOST_to_CPP(model, X, y, base_score):
    # Template for the C++ implementation
    codeInit="""

const int Nv = NvReplace;
const int dimX = dimXReplace;

float base_score =   base_score_Replace ;
float learning_rate = learning_rate_Replace ;

/////// Xy ////// 
const float X [] PROGMEM  = Xreplace;

const float y[] PROGMEM  = yreplace;



////////////////// TREES ////////////////////////////
////////////////////////////////////////////////////
TREES_CODE_replace

////////////////// XGBOOST MODEL //////////////////
///////////////////////////////////////////////////
float XGBpred(float X[]){
float out = 0;
XGBOOST_CODE_replace
out = out+base_score;
return out;}



void setup() {
Serial.begin(115200);
}

void loop() {
unsigned long timestart;
unsigned long timeend;
float Xi[dimX];
float yc;


Serial.println("Cal_Ardui,Expected,Delta_time(us)");
for (int l=0;l<Nv;l++){
for(int j = 0; j<dimX;j++){
Xi[j]=pgm_read_float_near(&X[l*dimX+j]);
}
timestart=micros();
yc=XGBpred(Xi);
timeend=micros();
Serial.print(yc);
Serial.print(",");
Serial.print(pgm_read_float_near(&y[l]),6);
Serial.print(",");
Serial.println(timeend-timestart);
}
Serial.println("====The End=====");
while(1);
}
"""
    
    
    
    if model.base_score is not None: 
        base_score = str(model.base_score)
    elif base_score is not None: 
        base_score = str(base_score)
    else : 
        base_score = "0"
    
    if model.learning_rate is not None: 
        learning_rate = str(model.learning_rate) 
    else: 
        learning_rate = "1" 
    learning_rate, base_score 


    N= model.n_estimators
    XGBOOST_CODE = code_trees(N, learning_rate)
    TREES_CODE = TreesCode(xgb_model)
    
    Nv, dimX= X.shape
    Nv, dimX= str(Nv), str(dimX)
    Xs=array_to_arduino(X.flatten())
    ys=array_to_arduino(y)

    codeInit= codeInit.replace("NvReplace",Nv)
    codeInit= codeInit.replace("dimXReplace",dimX)
    codeInit= codeInit.replace("Xreplace",Xs)
    codeInit= codeInit.replace("yreplace",ys)
    codeInit= codeInit.replace("base_score_Replace",base_score)
    codeInit= codeInit.replace("learning_rate_Replace",learning_rate)
    codeInit= codeInit.replace("TREES_CODE_replace", TREES_CODE)
    codeInit= codeInit.replace("XGBOOST_CODE_replace", XGBOOST_CODE)
    return codeInit



### DNN

def tf_model_to_arduino_code(inp_model, sub_X, sub_y, code):
    """
    This function converts a trained TensorFlow model into an Arduino-compatible code 
    for forward propagation. The model's weights, biases, and activation functions 
    are extracted, and Arduino code is generated to represent the model for use on 
    an embedded system.

    Inputs:
    - inp_model: Trained TensorFlow model (Keras model) whose layers and weights 
                 will be used for forward propagation.
    - sub_X: Input data (not used in the function directly, but likely required 
             for the context or future extension).
    - sub_y: Output data (not used directly, similar to `sub_X`).
    - code: Template code (as a string) that will be modified and returned, 
            with model weights, biases, and activation functions.

    Outputs:
    - code2: Arduino code with initialized model weights, biases, and forward 
             propagation logic embedded.
    """
    
    
    init_code="""
#include <math.h>
#include <Arduino.h>
#include <avr/pgmspace.h> // Include the PROGMEM functions

INIT_1

// Activation function///////////////
float sigmoid (float x){
    return 1./(1.+exp(-x));
}

float relu (float x){
    return max(x,0.);
}

float tanh_ (float x){ 
// make difference between tanh of C++ and tanh_ the activation func
    return tanh(x);
}

float linear(float x){
    return x;
}
///// You can add other activation function ////

void print_arr(float arr[], int N) {
    Serial.print("[");
    for (int i = 0; i < N; i++) {
        Serial.print(arr[i],4);
        if (i < N-1) {
            Serial.print(",");
            }
    }
    Serial.print("]");
}


void propagation(const float *WTf,  float *VEC, const float *B,float *out,  int M, int N, float (*act_func)(float)) {

  // Perform matrix-vector multiplication and activation
  for (int i = 0; i < M; ++i) {
    out[i] = pgm_read_float_near(&B[i]);
    for (int j = 0; j < N; ++j) {
      out[i] += pgm_read_float_near(&WTf[i * N + j]) * VEC[j];
    }
    out[i] = act_func(out[i]);
  }
}

void setup() {
  Serial.begin(115200);
}

void loop() {
unsigned long timestart;
unsigned long timeend;
float Xi[dimX];
INIT_2

Serial.println("Cal_Ardui,Expected,Delta_time(us)");
for (int l=0;l<Nv;l++){
for(int j = 0; j<dimX;j++){
    Xi[j]=pgm_read_float_near(&X[l*dimX+j]);
}
LOOP_
for (int k=0;k<M__final;k++){
Serial.print(OUTPUT__final[k],6);
Serial.print(" , ");
Serial.print(pgm_read_float_near(&y[l]),6);
Serial.print(" , ");
Serial.println(timeend-timestart);
}
}
Serial.println("====The End=====");
while(1);
}
"""
    WTfs = []  # List to store flattened weight matrices for each layer
    Bs = []  # List to store bias vectors for each layer
    acts = []  # List to store activation functions for each layer
    INIT = ""  # String to hold the initialization section of Arduino code
    
    # Loop through each layer of the model
    for i, layer in enumerate(inp_model.layers):
        W, B = layer.get_weights()  # Get weights and biases for the current layer
        WTf = W.T.flatten()  # Flatten the weight matrix and store it
        actfun = layer.activation.__name__  # Get the activation function name
        WTfs.append(WTf)  # Append flattened weights to the list
        Bs.append(B)  # Append biases to the list
        acts.append(actfun)  # Append activation function name to the list
        print("Layer", i, "W shape", W.shape, "Bias shape", B.shape, "Activation Function", actfun)

    # Define dimensions of weight matrix W
    M, N = W.T.shape

    # Get shape of the input data X (not used directly in the function)
    xshape = X.shape
    NvdimX = "const int Nv = " + str(xshape[0]) + ";\nconst int dimX = " + str(xshape[1]) + ";\n"

    # Convert X and y to Arduino-compatible format and store as strings
    Xystr = "\n/////// Xy ////// \nconst float X [] PROGMEM  = " + array_to_arduino(X.flatten()) + ";\n\n" + \
            "const float y[] PROGMEM  = " + array_to_arduino(y.flatten()) + " ;\n\n"

    initstr = ""  # String to hold initialization section for each layer
    
    # Loop through each layer again to generate initialization strings for weights and biases
    for i, layer in enumerate(inp_model.layers):
        W, B = layer.get_weights()  # Get weights and biases for the current layer
        M, N = W.T.shape  # Get dimensions of the weight matrix
        WTf = W.T.flatten()  # Flatten the weights

        # Prepare the Arduino code initialization for this layer
        Mstr = "const int M" + str(i) + " = " + str(M) + " ;"
        Nstr = "const int N" + str(i) + " = " + str(N) + " ;"
        WTfstr = "const float WTf" + str(i) + "[] PROGMEM  = " + str(WTf.tolist()).replace("[", "{").replace("]", "}") + " ;"
        Bstr = "const float BIAS" + str(i) + "[] PROGMEM= " + str(B.tolist()).replace("[", "{").replace("]", "}") + " ;"
        Outstr = "float OUTPUT" + str(i) + "[" + str(M) + "] ;"
        layerstr = "// Layer" + str(i) + " init \n" + Nstr + "\n" + Mstr + "\n" + WTfstr + "\n" + Bstr + "\n" + Outstr

        # Append the layer initialization to the overall initialization string
        initstr += layerstr + "\n\n"

    # Define the forward propagation logic in Arduino code
    prostr = "\n///////// Forward Propagation ////////////\ntimestart=micros();\n"
    funcstr = "propagation(WTf_, VEC, BIAS_, OUTPUT_, M_, N_,  activation); // Layer_\n"
    
    # Generate forward propagation code for each layer
    for i, layer in enumerate(inp_model.layers):
        W, B = layer.get_weights()  # Get weights and biases
        M, N = W.T.shape  # Get dimensions of the weight matrix
        WTf = W.T.flatten()  # Flatten the weights
        actfunc = layer.activation.__name__  # Get activation function name
        actfunc = actfunc.replace('tanh', 'tanh_')  # Replace 'tanh' with 'tanh_' for Arduino compatibility
        prostr += funcstr.replace("_", str(i)) \
            .replace('activation', actfunc) \
            .replace("VEC", "OUTPUT" + str(i - 1)) \
            .replace("OUTPUT-1", "Xi")

    # Final Arduino code section
    prostr += "timeend=micros();"
    
    # Replace placeholders in the code template with the generated code
    code2 = code.replace("INIT_1", NvdimX + initstr + Xystr)
    code2 = code2.replace("INIT_2", "")
    code2 = code2.replace("LOOP_", prostr)
    code2 = code2.replace("__final", str(i))  # Replace the final placeholder with the last layer index

    return code2  # Return the generated Arduino code
