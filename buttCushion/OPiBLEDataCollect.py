# This code collects data in the new format (4 %d \r\n) and collects in to save onto a csv file.
#In this script, test data is captured from buttBrick LIVE and printed.
from time import sleep
import time
import pandas as pd
import numpy as np
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
import pandas as pd
import re
import csv
import os
import sys

ble = BLERadio()

def uart_read(): # returns raw data from buttBrick and calls itself recursively in case of error
    data = re.split("\s", uart_service.readline().decode("utf-8").replace("\r\n",""))
    if not (len(data) == 4): # if there is incomplete number of datapoints in array
        data = uart_read()
    for element in data:
        if not (element.isdigit()): # if one of the elements is not a number
            print("error in data format")
            data = uart_read()        
    return data

def read_array():
    inputList = []
    for i in uart_read():
        inputData = float(i) * 0.0000125885 # 3.3 / 262144
        inputList.append(inputData)
    print(inputList)
    return inputList

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

def run_collection():
    testPosition = 1
    SampleBatchSize = 5 # number of samples to capture everytime script is run
    fileLabelCounter = 1 # file name uniquifyer
    sampleCounter = 0 # counts the number of 4-reading samples

    testDf = pd.DataFrame(columns=['1','2','3','4','Posture'])

    inputList = []
    for testPosition in range(1, 6):
        for run in range(5):
            print(f"Starting run {run +1} with position {testPosition}")
            print("RESET POSITION")
            inputData = ""

            for count in range(1, 21):
                sys.stdout.write('\r{}'.format(count))  # Write the current count without newline
                sys.stdout.flush()  # Flush the output buffer
                count += 1
                sleep(1)  # Wait for 1 second
                if (count == 10):
                    sys.stdout.flush()  # Flush the output buffer
                    print("RETURN TO POSITION")
                    if (testPosition == 1):
                        print("Sit UPRIGHT")
                    elif (testPosition == 2):
                        print("SLOUCH")
                    elif (testPosition == 3):
                        print("MOVE FORWARD")
                    elif (testPosition == 4):
                        print("LEAN LEFT")
                    elif (testPosition == 5):
                        print("LEAN RIGHT")

            print("SAVING STARTS HERE")
            start_time = time.time()

            while sampleCounter < SampleBatchSize: # Gets 10 samples of 4-reading samples
                try:
                    inputList = uart_read_array()
                except ConnectionError:
                    return 
                sampleCounter += 1
                testDf.loc[len(testDf)] = [inputList[0], inputList[1], inputList[2], inputList[3], testPosition]
                print(inputList)
                inputList.clear()
            elapsed_time = time.time() - start_time
            print(f"Run {run+1} completed. Elapsed time: {elapsed_time:.2f} seconds")
            sampleCounter = 0

    folder_path = 'csv_files/'
    filename = 'test_data.csv'
    while os.path.exists(folder_path+filename):
        filename = f'dataset_{fileLabelCounter}.csv'
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
