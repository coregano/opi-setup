#In this script, test data is captured LIVE and printed.
from time import sleep
import time
import pandas as pd
import numpy as np
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
import pandas as pd
import numpy as np
import csv
import os
import sys

ble = BLERadio()

def run_collection():
    testPosition = 4 # position that person is sitting in. 1 = hunch, 2 = normal, 3 =  left lean, 4 = right lean

    SampleBatchSize = 10 # number of samples to capture everytime script is run
    fileLabelCounter = 1 # file name uniquifyer
    sampleCounter = 0 # counts the number of 4-reading samples

    testDf = pd.DataFrame(columns=['1','2','3','4','Posture','Dataset'])
    max_value = 0.1

    inputList = []
    running = True
    for run in range(10):
        print(f"Starting run {run +1}...")
        print("RESET POSITION")
        inputData = ""

        for count in range(1, 61):
            sys.stdout.write('\r{}'.format(count))  # Write the current count without newline
            sys.stdout.flush()  # Flush the output buffer
            count += 1
            sleep(1)  # Wait for 1 second
            if (count == 50):
                sys.stdout.flush()  # Flush the output buffer
                print("RETURN TO POSITION")
               
        print("SAVING STARTS HERE")
        start_time = time.time()
        
        while inputData != "N": # This loop forces the program to wait until the data resets. an "N" means the last value has been sent and you can reset the list
            inputData = uart_service.readline().decode("utf-8")
            inputData = inputData.replace("\r\n","") # Remove special characters
            # inputData = inputData.rstrip() # Remove special characters
            print(inputData)

        while sampleCounter < SampleBatchSize: # Gets 10 samples of 4-reading samples
            inputData = uart_service.readline().decode("utf-8") 
            inputData = inputData.replace("\r\n","") # Remove special characters       
            # inputData = inputData.rstrip() # Remove special characters
            
            if inputData != 'N': # If the value read from serial is not an N, that means it is a valid sensor reading, and should be appended to the sensor reading list.
                inputData = float(inputData) * 3.3 / (4096 * 64) # Convert binary reading to values that the model was trained on.
                inputList.append(inputData) 
                print(inputData)

            else: # If value read from uart is an N, that means that a batch of 4 sensor values were sent out.
                # xTest = pd.DataFrame(data=[inputList], columns=['1','2','3','4']) # Send all sensor readings in the list to a dataframe
                print(inputList)
                sampleCounter += 1
                testDf.loc[len(testDf)] = [inputList[1], inputList[2], inputList[3], inputList[0], testPosition, run]
                inputList.clear()
        elapsed_time = time.time() - start_time
        print(f"Run {run+1} completed. Elapsed time: {elapsed_time:.2f} seconds")
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

    # # Label the four new rows in the 'Dataset' column
    # testDf.loc[-1, 'Dataset'] = 'mean'
    # testDf.loc[-2, 'Dataset'] = 'var'
    # testDf.loc[-3, 'Dataset'] = 'min'
    # testDf.loc[-4, 'Dataset'] = 'max'
    # ##########################################################

    folder_path = '/home/user/proj/buttCushion/csv_files/24cm/'
    filename = '24cm_butt_data_1.csv'
    while os.path.exists(folder_path+filename):
        filename = f'24cm_butt_data_{fileLabelCounter}.csv'
        fileLabelCounter += 1
    print(folder_path+filename)
    testDf.to_csv(folder_path + filename, index=False)
    print("SAVE DONE")
    exit()

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
        while uart_connection.connected:
            run_collection()    
            exit()
