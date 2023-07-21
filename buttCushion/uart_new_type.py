from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
import pygame
import pandas as pd
import numpy as np
import re

ble = BLERadio()
max_value = 0.1
    
def display_screen():
    pygame.init()
    screen_size = (600,600)
    square_color = (0,255,0)
    screen = pygame.display.set_mode(screen_size)
    running = True
    square_size = screen_size[0]//2
    arr2d = np.zeros((2,2))

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # User clicked close button
                running = False

        arr2d = np.reshape(read_array(), (2,2))
        if np.all(arr2d == 0):
            arr2d.fill(0.001)

        for row in range(2):
            for col in range(2):
                green_value = int(arr2d[row][col] * 255 / max_value)
                square_color = (0, green_value, 0)
                pygame.draw.rect(screen, square_color, pygame.Rect(col * square_size, row * square_size, square_size, square_size))
        
        pygame.display.flip()

    pygame.quit()
    
def uart_read(): # returns raw data from buttBrick and calls itself recursively in case of error
    data = re.split("\s", uart_service.readline().decode("utf-8").replace("\r\n",""))
    print(data)
    if not (data.len() == 4): # if there is incomplete number of datapoints in array
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

def switcharoo (inputList):
    newInputList = [inputList[1], inputList[2], inputList[0], inputList[3]]
    return newInputList

#################################################################################################
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
            display_screen()
            break
