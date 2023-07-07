#In this script, test data is captured LIVE and printed.
# import pygame
from time import sleep
import time
import pandas as pd
import numpy as np
import serial
import csv
import os
import sys

folder_path = '/home/user/proj/buttCushion/csv_files/24cm/'
filename = '24cm_butt_data_1.csv'

testPosition = 4 # position that person is sitting in. 1 = hunch, 2 = normal, 3 =  left lean, 4 = right lean

SampleBatchSize = 10 # number of samples to capture everytime script is run
fileLabelCounter = 1 # file name uniquifyer
sampleCounter = 0 # counts the number of 4-reading samples
serialport = serial.Serial('/dev/ttyACM0',baudrate=9600,timeout=2)

screen_size = (300,300)
background_color = (255,255,255)
square_color = (0,255,0)
quit_button_color = (255,0,0)

testDf = pd.DataFrame(columns=['1','2','3','4','Posture','Dataset'])
# testlist = [1,2,3,4]
# testDf.loc[len(testDf)] = testlist
# print(testDf)
# testDf.columns = ['1','2','3','4']
inputData = 0
inputList = []

#If this line is reached, that means a new sensor dataset is about to be sent out. the next 18 values will be sensor readings.
for run in range(10):
    print(f"Starting run {run +1}...")
    print("RESET POSITION")
    inputData = ""
    # Close the serial port if it is already open
    if serialport.is_open:
        serialport.close()
    for count in range(1, 61):
        sys.stdout.write('\r{}'.format(count))  # Write the current count without newline
        sys.stdout.flush()  # Flush the output buffer
        count += 1
        sleep(1)  # Wait for 1 second
        if (count == 50):
            print("RETURN TO POSITION")
            # Open the serial port again
            serialport = serial.Serial('/dev/ttyACM0', baudrate=9600, timeout=2)

    print("SAVING STARTS HERE")
    start_time = time.time()

    # Flush the input buffer
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

        else: # If value read from serial is an N, that means that a batch of 4 sensor values were sent out.
            # xTest = pd.DataFrame(data=[inputList], columns=['1','2','3','4']) # Send all sensor readings in the list to a dataframe
            print(inputList)
            sampleCounter += 1
            testDf.loc[len(testDf)] = [inputList[1], inputList[2], inputList[3], inputList[0], testPosition, run]
            inputList.clear()
    elapsed_time = time.time() - start_time
    print(f"Run {run+1} completed. Elapsed time: {elapsed_time:.2f} seconds")
    sampleCounter = 0

##########################################################
# Exclude first row (labels) for statistics calculations
data_rows = testDf.iloc[1:]

# Calculate and append statistics rows across columns
mean_row = data_rows.mean(axis=0)
var_row = data_rows.var(axis=0)
min_row = data_rows.min(axis=0)
max_row = data_rows.max(axis=0)

testDf.loc[-1] = mean_row
testDf.loc[-2] = var_row
testDf.loc[-3] = min_row
testDf.loc[-4] = max_row

# Label the four new rows in the 'Dataset' column
testDf.loc[-1, 'Dataset'] = 'mean'
testDf.loc[-2, 'Dataset'] = 'var'
testDf.loc[-3, 'Dataset'] = 'min'
testDf.loc[-4, 'Dataset'] = 'max'
##########################################################

while os.path.exists(folder_path+filename):
    filename = f'24cm_butt_data_{fileLabelCounter}.csv'
    fileLabelCounter += 1
print(folder_path+filename)
testDf.to_csv(folder_path + filename, index=False)
print("SAVE DONE")
