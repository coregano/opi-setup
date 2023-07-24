# this code will take in 4%d format from BB and use a forest developed from pre-collected code and also do a live prediction of the current posture
#In this script, test data is captured LIVE and printed. Roll back to this version if anything screws up.
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn import metrics
from time import sleep
import pandas as pd
import numpy as np
import re
from sklearn.metrics import confusion_matrix
import pickle
# import seaborn as sns
# import matplotlib.pyplot as plt

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

# filesave location
folderPathOPi = '/home/user/Documents/opi-setup/buttCushion/'
# Load the saved decision tree model
forestFile = 'decision_tree_model.pkl'

def make_forest(): 
    xDataframe, yDataFrame = createTrainingSet()
    x_train, x_test, y_train, y_test = train_test_split(xDataframe, yDataFrame, test_size=0.2, random_state=42)

    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(x_train, y_train)

    y_pred = rf.predict(x_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(accuracy)
    return rf

def uart_read(): # returns raw data from buttBrick and calls itself recursively in case of error
    data = re.split("\s", uart_service.readline().decode("utf-8").replace("\r\n",""))
    if not (len(data) == 4): # if there is incomplete number of datapoints in array
        data = uart_read()
    for element in data:
        if not (element.isdigit()): # if one of the elements is not a number
            print("error in data format")
            data = uart_read()        
    return data

def uart_read_array(): # returns raw data from buttBrick and calls itself recursively in case of error
    inputList = []
    data_format = r'^(\d+\s){3}\d+$'
    data = uart_service.readline().decode("utf-8").replace("\r\n","")
    while not re.match(data_format, data):
        if not uart_connection or not uart_connection.connected:
            raise ConnectionError("Bluetooth disconnected. Repairing...")

        else:
            print("Error in data format. Rereading....")
            data = uart_service.readline().decode("utf-8").replace("\r\n","")
    data = re.split("\s", data)
    print(data)
    for dPoint in data:
        dPoint = float(dPoint) * 0.0000125885
        inputList.append(dPoint)
    return inputList

def read_array():
    inputList = []
    for i in uart_read():
        inputData = float(i) * 0.0000125885 # 3.3 / 262144
        inputList.append(inputData)
    print(inputList)
    return inputList

def createTrainingSet():
    path = '/home/user/Documents/opi-setup/csv_files/'
    #how to filter data?
    # unreliable prototype
    # issue with forest? - check using y_pred
    
    ##################################################################################################
    combinedDf = pd.read_csv(path + 'dataset_1.csv')
    ##################################################################################################

    # Separate the input features (xDf) and labels (yDf)
    xDf = combinedDf.iloc[:, 0:4]
    yDf = combinedDf.iloc[:, 4]
    print("input columns")
    return xDf, yDf

def CM_plot(y_real, y_pred): # plots the confusion matrix for a given prediction set with the intented postures
    cm = confusion_matrix(y_real, y_pred)
    print("Confusion Matrix:")
    print(cm)
    
    # Plot the confusion matrix using seaborn
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title("Confusion Matrix")
    plt.show()

def confidence_analysis(y_pred_prob): # prints out predicted posture with the confidence    
    print("Confidence of Predictions:")
    for i, prob in enumerate(y_pred_prob):
        predicted_class = clf.classes_[np.argmax(prob)]
        confidence = prob[np.argmax(prob)]
        print(f"Sample {i+1}: Predicted Class={predicted_class}, Confidence={confidence}")

def run_forest(clf):
    while True:
    #If this line is reached, that means a new sensor dataset is about to be sent out. the next 18 values will be sensor readings.
        try:
            xTest = pd.DataFrame(data=[uart_read_array()], columns=['1','2','3','4']) # Send all sensor readings in the list to a dataframe
        except ConnectionError:
            return
        print(xTest)
        # y_pred = clf.predict(xTest) # Predict what the posture is from the 18 sensor values
        # print(y_pred)
            # After making all the predictions
        y_pred_prob = clf.predict_proba(xTest)
        predicted_class = clf.classes_[np.argmax(y_pred_prob)]
        confidence = y_pred_prob[0][np.argmax(y_pred_prob)]
        # Print the confidence of the predictions
        print(f"\n###############################################\n{predicted_class}, {confidence}\n###############################################\n")
        sleep(2)


uart_connection = None
ble = BLERadio()
while True:
    if not uart_connection:
        print("Trying to connect...")

        for adv in ble.start_scan(ProvideServicesAdvertisement):
            if UARTService in adv.services:
                uart_connection = ble.connect(adv)
                print("Connected")
                break
        ble.stop_scan()

    if uart_connection and uart_connection.connected:
        uart_service = uart_connection[UARTService]
        clf = make_forest() 
        filename = 'decision_tree_model.pkl'
        # Save the model to a file
        joblib.dump(clf, 'decision_forest_model.joblib')  
        # clf = pickle.load(open(folderPathOPi + forestFile, 'rb'))
        pickle.dump(clf, open(filename, 'wb'))
        while uart_connection.connected:
            run_forest(clf)
            # Save the decision tree model
