from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
import pygame
import pandas as pd
import numpy as np

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

    while (uart_read() != "1"): # This loop forces the program to wait until the data resets. 
        uart_read()

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
    
def uart_read():
    data = uart_service.readline().decode("utf-8").replace("\r\n","")
    if not (data.isdigit()):
        print(data)
        raise TypeError ("Error in data transfer. Rereading...")
    return data
    
def read_array():
    inputList = []
    for i in range(4):
        inputData = float(uart_read()) * 0.0000125885 # 3.3 / 262144
        if inputData >= max_value: # ensure data does not overflow the max value of 255
            inputData = max_value
        inputList.append(inputData)
    inputList = switcharoo(inputList) # rearrangement of inputList from read_array()
    print(inputList)
    uart_read()
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