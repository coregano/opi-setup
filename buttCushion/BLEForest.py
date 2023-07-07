#In this script, test data is captured LIVE and printed. Roll back to this version if anything screws up.
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn import metrics

from time import sleep
import pandas as pd
import numpy as np
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
import pandas as pd
import numpy as np

ble = BLERadio()

def make_forest():
    
    xDataframe, yDataFrame = createTrainingSet()
    #Validation dataset with all positions in one dataset
    # validationDf =  pd.read_csv('all_external_ppl_test.csv')
    # validationDf = validationDf.drop_duplicates()
    x_train, x_test, y_train, y_test = train_test_split(xDataframe, yDataFrame, test_size=0.2, random_state=42)
    # x_train, x_validate, y_train, y_validate = train_test_split(xDf, yDf, test_size=0.2)

    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(x_train, y_train)

    y_pred = rf.predict(x_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(accuracy)
    return rf


def createTrainingSet():
    path = '/home/user/proj/buttCushion/csv_files/24cm/'

    #how to filter data?
    # unreliable prototype
    # issue with forest? - check using y_pred
    # pos0Df = pd.read_csv(path + '24cm_butt_data_1.csv')
    # #first position training and test dataset
    # pos1Df = pd.read_csv(path + '24cm_butt_data_2.csv')
    # #second position training and test dataset
    # pos2Df = pd.read_csv(path + '24cm_butt_data_3.csv')
    # #third position training and test dataset
    # pos3Df = pd.read_csv(path + '24cm_butt_data_4.csv')
    # #fourth position training and test dataset
    # print("reading done")

    # #combine datasets into one
    # # combinedDf = pd.concat([pos0Df,pos1Df, pos2Df, pos3Df, pos4Df])
    # combinedDf = pd.concat([pos0Df, pos1Df, pos2Df, pos3Df], ignore_index=42)

    #remove duplicate data
    # combinedDf = combinedDf.drop_duplicates()

    combinedDf = pd.read_csv(path + '24cm_lisa_data.csv')
    # Separate the input features (xDf) and labels (yDf)
    xDf = combinedDf.iloc[:, 0:4]
    yDf = combinedDf.iloc[:, 4]
    print("input columns")
    return xDf, yDf

def run_forest(clf):
    inputData = 0
    inputList = []

    while True:
    #If this line is reached, that means a new sensor dataset is about to be sent out. the next 18 values will be sensor readings.
        inputData = uart_service.readline().decode("utf-8")
        inputData = inputData.replace("\r\n","") # Remove special characters
        print(inputData)
        if inputData != "N":
            inputData = float(inputData) * 3.3 / (4096 * 64) #Convert binary reading to values that the model was trained on.
            inputList.append(inputData)
            
            # print(inputList)     

        else: # If value read from serial is an N, that means that a batch of 4 sensor values were sent out.
            arrangedList = [inputList[1], inputList[2], inputList[3], inputList[0]]
            print("n")
            xTest = pd.DataFrame(data=[arrangedList], columns=['1','2','3','4']) # Send all sensor readings in the list to a dataframe
            
            print(xTest)
            y_pred = clf.predict(xTest) # Predict what the posture is from the 18 sensor values

            if y_pred == 1:
                postureResult = 'hunch'
            elif y_pred == 2:
                postureResult = 'normal'
            elif y_pred == 3:
                postureResult = 'lean left'
            elif y_pred == 4:
                postureResult = 'lean right'
            print(y_pred)
            inputList.clear()
        # print("Accuracy: ", metrics.accuracy_score(yValidationDf,y_pred))
        # print(y_pred)

uart_connection = None

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
        while uart_connection.connected:
            run_forest(clf)
