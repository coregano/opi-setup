#In this script, test data is captured LIVE and printed.
# import pygame
import pandas as pd
import numpy as np
import serial
import csv
import os

folder_path = '/home/user/proj/buttCushion/csv_files/24cm/'
filename = 'data_1.csv'

testPosition = 4 # position that person is sitting in. 1 = hunch, 2 = normal, 3 =  left lean, 4 = right lean

SampleBatchSize = 10 # number of samples to capture everytime script is run
fileLabelCounter = 1 # file name uniquifyer
sampleCounter = 0 # counts the number of 4-reading samples
serialport = serial.Serial('/dev/ttyACM0',baudrate=9600,timeout=2)

screen_size = (300,300)
background_color = (255,255,255)
square_color = (0,255,0)
quit_button_color = (255,0,0)

testDf = pd.DataFrame(columns=['1','2','3','4'])
# testlist = [1,2,3,4]
# testDf.loc[len(testDf)] = testlist
# print(testDf)
# testDf.columns = ['1','2','3','4']
inputData = 0
inputList = []

while inputData != "N": # This loop forces the program to wait until the data resets. an "N" means the last value has been sent and you can reset the list
    inputData = serialport.readline().decode('ascii') # Read from serial
    inputData = inputData.replace("\r\n","") # Remove special characters


print("SAVING STARTS HERE")
#If this line is reached, that means a new sensor dataset is about to be sent out. the next 18 values will be sensor readings.
while sampleCounter < SampleBatchSize: # Gets 30 samples of 4-reading samples
    inputData = serialport.readline().decode('ascii') # Read from serial
    inputData = inputData.replace("\r\n","") # Remove special characters
    
    if inputData != 'N': # If the value read from serial is not an N, that means it is a valid sensor reading, and should be appended to the sensor reading list.
        inputData = float(inputData) * 3.3 / 4096 #Convert binary reading to values that the model was trained on.
        inputList.append(inputData)
        print(sampleCounter)

     #   print(inputList)     
    else: # If value read from serial is an N, that means that a batch of 18 sensor values were sent out.
        print(inputList)
        #xTest = pd.DataFrame(data=[inputList], columns=['1','2','3','4']) # Send all sensor readings in the list to a dataframe
        inputList[1], inputList[2] = inputList[2], inputList[1]
        testDf.loc[len(testDf)] = inputList
        sampleCounter += 1
        inputList.clear()

testDf['Posture'] = testPosition
print(testDf)
print(folder_path+filename)

while os.path.exists(folder_path+filename):
    filename = f'data_{fileLabelCounter}.csv'
    fileLabelCounter += 1
testDf.to_csv(folder_path + filename, index=False)
print("SAVE DONE")
