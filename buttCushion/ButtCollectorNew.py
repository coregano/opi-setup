#In this script, test data is captured LIVE and printed.
# import pygame
from time import sleep
import time
import pandas as pd
import numpy as np
import serial
import csv
import os

folder_path = '/home/user/proj/buttCushion/csv_files/24cm/'
filename = '24_butt_data_1.csv'

testPosition = 1 # position that person is sitting in. 1 = hunch, 2 = normal, 3 =  left lean, 4 = right lean

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

#If this line is reached, that means a new sensor dataset is about to be sent out. the next 18 values will be sensor readings.
for run in range(10):
    # Flush the input buffer
    print(f"Starting run {run +1}...")
    IL, OL, IR, OR = (0.0, 0.0, 0.0, 0.0)
    inputData = ""
    for j in range(1, 61):
        print(j)
        sleep(1)

    print("SAVING STARTS HERE")
    start_time = time.time()
    serialport.reset_input_buffer()
    while inputData != "N": # This loop forces the program to wait until the data resets. an "N" means the last value has been sent and you can reset the list
        inputData = serialport.readline().decode('ascii') # Read from serial
        inputData = inputData.replace("\r\n","") # Remove special characters

    while sampleCounter < SampleBatchSize: # Gets 10 samples of 4-reading samples
        inputData = serialport.readline().decode('ascii') # Read from serial
        inputData = inputData.replace("\r\n","") # Remove special characters
        
        if inputData != 'N': # If the value read from serial is not an N, that means it is a valid sensor reading, and should be appended to the sensor reading list.
            inputData = float(inputData) * 3.3 / 4096 # Convert binary reading to values that the model was trained on.
            inputList.append(inputData)
            # print(sampleCounter)

        else: # If value read from serial is an N, that means that a batch of 18 sensor values were sent out.
            # xTest = pd.DataFrame(data=[inputList], columns=['1','2','3','4']) # Send all sensor readings in the list to a dataframe
            print(inputList)
            OL += inputList[1]
            OR += inputList[2]
            IL += inputList[3]
            IR += inputList[0]
            sampleCounter += 1
            inputList.clear()

    elapsed_time = time.time() - start_time
    totalSet = [IL, OL, OR, IR]
    averageSet = []
    for number in totalSet:
        averageSet.append(round(number/10, 5))

    print(averageSet)
    print("RESET POSITION")
    print(f"Run {run+1} completed. Elapsed time: {elapsed_time:.2f} seconds")

    testDf.loc[len(testDf)] = averageSet
    sampleCounter = 0

# ##########################################################
# # Exclude first row (labels) for statistics calculations
# data_rows = testDf.iloc[1:]

# # Calculate and append statistics rows across columns
# mean_row = data_rows.mean(axis=0)
# var_row = data_rows.var(axis=0)
# min_row = data_rows.min(axis=0)
# max_row = data_rows.max(axis=0)

# testDf.loc[-1] = mean_row
# testDf.loc[-2] = var_row
# testDf.loc[-3] = min_row
# testDf.loc[-4] = max_row

# # Sort the DataFrame based on index
# testDf.sort_index(inplace=True)

# # Label the four new rows in the 'Posture' column
# testDf.loc[-1, 'Posture'] = 'mean'
# testDf.loc[-2, 'Posture'] = 'var'
# testDf.loc[-3, 'Posture'] = 'min'
# testDf.loc[-4, 'Posture'] = 'max'
# ##########################################################

testDf['Posture'] = testPosition
print(testDf)
print(folder_path+filename)

while os.path.exists(folder_path+filename):
    filename = f'data_{fileLabelCounter}.csv'
    fileLabelCounter += 1
testDf.to_csv(folder_path + filename, index=False)
print("SAVE DONE")
