# SPDX-FileCopyrightText: 2020 Dan Halbert for Adafruit Industries
#
# SPDX-License-Identifier: MIT

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
import pygame
import pandas as pd
import numpy as np

ble = BLERadio()

def switcharoo (inputList):
    newInputList = [inputList[1], inputList[2], inputList[0], inputList[3]]
    return newInputList
    
def run_reader():
    pygame.init()
    screen_size = (600,600)
    square_color = (0,255,0)
    screen = pygame.display.set_mode(screen_size) 
    running = True
    square_size = screen_size[0]//2
    arr2d = np.zeros((2,2))

    max_value = 0.1

    inputList = []
    inputData = 0
    while inputData != "1": # This loop forces the program to wait until the data resets. an "N" means the last value has been sent and you can reset the list
        inputData = uart_service.readline().decode("utf-8")
        print(inputData)
        inputData = inputData.replace("\r\n","") # Remove special characters

    #If this line is reached, that means a new sensor dataset is about to be sent out. the next 18 values will be sensor readings.
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # User clicked close button
                running = False
                
        inputData = uart_service.readline().decode("utf-8") 
        inputData = inputData.replace("\r\n","") # Remove special characters       
        if inputData != "1": # If the value read from serial is not an N, that means it is a valid sensor reading, and should be appended to the sensor reading list.
            inputData = float(inputData) * 3.3 / (4096 * 64) # Convert binary reading to values that the model was trained on.
            print(inputData)

            # If sensor processed value is larger than expected max value, keep value at max value
            if inputData >= max_value:
                inputData = max_value
            inputList.append(inputData)
        
        
        else: # If value read from serial is an N, that means that a batch of 18 sensor values were sent out.
        
            print(inputList)
            inputList = switcharoo(inputList) # rearrangement of input data
            arr2d = np.reshape(inputList,(2,2))

            if np.all(arr2d==0):
                arr2d.fill(0.001)

            #print(arr2d)

            for row in range(2):
                for col in range(2):
                    green_value = int(arr2d[row][col]*255/max_value)
                    square_color = (0, green_value, 0)
                    pygame.draw.rect(screen, square_color, pygame.Rect(col * square_size, row * square_size, square_size, square_size))
            
            pygame.display.flip()
            inputList.clear()

    # print("Accuracy: ", metrics.accuracy_score(yValidationDf,y_pred))
    # print(y_pred)
    pygame.quit()

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
            run_reader()    
            break
