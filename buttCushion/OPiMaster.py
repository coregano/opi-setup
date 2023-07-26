# This is the master code that will run in the OPi during actual prototype testing.
import pandas as pd
import joblib
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import accuracy_score
# from sklearn import metrics
import time
from time import sleep
import pandas as pd
import numpy as np
import re
import os
import sys
import pickle
# import seaborn as sns
# import matplotlib.pyplot as plt
import digitalio
import board
from PIL import Image, ImageDraw
from adafruit_rgb_display import ili9341
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

# variable to check for first run
isFirstRun = True

# filesave location
folderPathOPi = '/home/orangepi/opi-setup/buttCushion/'

# file name uniquifyer
fileLabelCounter = 1 

# Load the saved decision tree model
forestFile = 'decision_forest_model.joblib'
# clf = pickle.load(open(folderPathOPi + forestFile, 'rb'))
clf = joblib.load(folderPathOPi + forestFile)

# Configuration for CS and DC pins:
cs_pin = digitalio.DigitalInOut(board.PC11)
dc_pin = digitalio.DigitalInOut(board.PC6)
reset_pin = digitalio.DigitalInOut(board.PC9)
# Configuration for touch
touch_pin = digitalio.DigitalInOut(board.PC14)

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 24000000
# Setup SPI bus using hardware SPI:
spi = board.SPI()
disp = ili9341.ILI9341(
    spi,
    rotation=90,  
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
if disp.rotation % 180 == 90:
    height = disp.width  # we swap height/width to rotate it to landscape!
    width = disp.height
else:
    width = disp.width 
    height = disp.height
image = Image.new("RGB", (width, height))
# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)
# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image)

# scales, crops and centers the image for display
def image_prep(filename): 
    image = Image.open(filename)
    # Scale the image to the smaller screen dimension
    image_ratio = image.width / image.height
    screen_ratio = width / height
    if screen_ratio < image_ratio:
        scaled_width = image.width * height // image.height
        scaled_height = height
    else:
        scaled_width = width
        scaled_height = image.height * width // image.width
    image = image.resize((scaled_width, scaled_height), Image.Resampling.BICUBIC)

    # Crop and center the image
    x = scaled_width // 2 - width // 2
    y = scaled_height // 2 - height // 2
    image = image.crop((x, y, x + width, y + height))
    return image

# prepare images for display
image0 = image_prep(folderPathOPi + "0.jpg")
image1 = image_prep(folderPathOPi + "1.png")
image2 = image_prep(folderPathOPi + "2.png")
image3 = image_prep(folderPathOPi + "3.png")
image4 = image_prep(folderPathOPi + "4.png")
image5 = image_prep(folderPathOPi + "5.png")
image6 = image_prep(folderPathOPi + "6.png")

# Reads off an csv file to create input and result columns for the decision tree
def createTrainingSet():
    pathPC = '/home/user/Documents/opi-setup/buttCushion/csv_files/'
    pathOPi = '/home/orangepi/opi-setup/buttCushion/'

    ##################################################################################################
    combinedDf = pd.read_csv(pathPC + 'dataset_1.csv')
    ##################################################################################################

    # Separate the input features (xDf) and labels (yDf)
    xDf = combinedDf.iloc[:, 0:4]
    yDf = combinedDf.iloc[:, 4]
    print("input columns")
    return xDf, yDf

# prints out predicted posture with confidence 
def confidence_analysis(y_pred_prob):    
    print("Confidence of Predictions:")
    for i, prob in enumerate(y_pred_prob):
        predicted_class = clf.classes_[np.argmax(prob)]
        confidence = prob[np.argmax(prob)]
        print(f"Sample {i+1}: Predicted Class={predicted_class}, Confidence={confidence}")

# using a forest, runs it with live received data
def run_forest():
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

# uses decision tree to predict user posture
def read_posture():
    runs = 20 # number of predictions to be made
    postureDataSet = np.empty((0,5))
    for i in range(runs):
        postureData = []
        try:
            datapoints = uart_read_array()
            xData = pd.DataFrame(data=[datapoints], columns=['1','2','3','4']) # Send all sensor readings in the list to a dataframe
        except ConnectionError:
            raise ConnectionError
        print(xData)
        prediction = clf.predict(xData)
        postureData = np.append(datapoints, prediction)
        postureDataSet = np.vstack((postureDataSet, postureData))
    return postureDataSet


# reads raw data from buttBrick and reads continuously in case of error 
# raises ConnectionError when bluetooth disconnects
def uart_read_array(): 
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

# # saves a dataframe as a csv file into the device.
# def save_csv(csvDf):
#     filename = 'test_data.csv'
#     while os.path.exists(folder_path+filename):
#         filename = f'dataset_{fileLabelCounter}.csv'
#         fileLabelCounter += 1
#     print(folder_path+filename)
#     csvDf.to_csv(folder_path + filename, index=False)
#     print("SAVE DONE")

# returns whether the user is sitting on the cushion
def isPresent():
    presenceCheckRuns = 20
    presenceCounter = 0
    threshold = 0.01
    presenceStartTime = time.time()
    for i in range(presenceCheckRuns):
        presenceCounter += int(threshold < np.mean(uart_read_array()))
    presenceTime = time.time() - presenceStartTime
    print(presenceTime)
    if (presenceCounter >= presenceCheckRuns - 5):
        return True
    else:
        return False

# code to be run when the user is sitting on the cushion for the first time after bootup 
def first_run():
    calibration_set = pd.DataFrame(columns=['1','2','3','4','Posture'])
    SampleBatchSize = 5
    sampleCounter = 0
    print("SAVING STARTS HERE")
    start_time = time.time()
    while sampleCounter < SampleBatchSize: # Gets 10 samples of 4-reading samples
        try:
            inputList = uart_read_array()
        except ConnectionError:
            return 
        sampleCounter += 1
        calibration_set.loc[len(calibration_set)] = [inputList[0], inputList[1], inputList[2], inputList[3], 1]
        print(inputList)
        inputList.clear()
    elapsed_time = time.time() - start_time

# prompts the user to check if the predicted posture is correct
def isTouch():
    press_count = 0
    for i in range (10):
        press_count += int(touch_pin.value)
        sleep (0.5)
    if (press_count > 3):
        return True
    else:
        return False
    
# mainframe of code 
# if code reaches this function, it means that the user is sitting on the cushion. 
def run_posture():
    inputDf = pd.DataFrame(columns=['1','2','3','4','Posture','Press'])
    dataDf = read_posture()
    goodPostureCount = np.sum(dataDf[:, 4] == 1) # count the occurance of 1
    if (goodPostureCount > len(dataDf) // 2): # more than half of predictions are 1
        disp.image(image5)
        print("good")
    else:
        disp.image(image6)
        print("bad")
    
    if (isTouch()):
        disp.image(image0)
        print("touched")
    else:
        print("no touch")
    
uart_connection = None
ble = BLERadio()
# the main bluetooth connection loop
while True:
    if not uart_connection:
        print("Trying to connect...")
        disp.image(image1)
        for adv in ble.start_scan(ProvideServicesAdvertisement):
            if UARTService in adv.services:
                uart_connection = ble.connect(adv)
                print("Connected")
                break
        ble.stop_scan()

    if uart_connection and uart_connection.connected:
        # bluetooth connected
        uart_service = uart_connection[UARTService]
        disp.image(image2)
        while uart_connection.connected:
            if not (isPresent()): # no user present, run the main loop again
                disp.image(image3)
                continue 
            disp.image(image4)
            run_posture()
            # if (isFirstRun):
            #     first_run()
            # else:
            #     run_posture(clf)
