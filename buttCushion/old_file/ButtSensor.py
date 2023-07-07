#In this script, test data is captured LIVE and printed.
import pygame
import pandas as pd
import numpy as np
import serial

serialport = serial.Serial('/dev/ttyACM0',baudrate=9600,timeout=2)
# inputData = serialport.readline().decode('ascii')
screen_size = (600,600)
background_color = (255,255,255)
square_color = (0,255,0)
# quit_button_color = (255,0,0)

#max value that we expect to read from the sensors after the *3.3/4096 step
max_value = 0.1

inputData = 0
inputList = []
arr2d = np.zeros((2,2))
pygame.init()

screen = pygame.display.set_mode(screen_size)

square_size = screen_size[0]//2
# quit_button_rect = pygame.Rect(screen_size[0]//2-50,screen_size[1]-50,100,40)
#font = pygame.font.Font(None,36)

#Validation dataset with all positions in one dataset
# validationDf =  pd.read_csv('all_external_ppl_test.csv')
# validationDf = validationDf.drop_duplicates()

running = True

def switcharoo (inputList) :
    newInputList = [inputList[1], inputList[2], inputList[3], inputList[0]]
    return newInputList
    


while inputData != "N": # This loop forces the program to wait until the data resets. an "N" means the last value has been sent and you can reset the list
    inputData = serialport.readline().decode('ascii') # Read from serial
    inputData = inputData.replace("\r\n","") # Remove special characters

#If this line is reached, that means a new sensor dataset is about to be sent out. the next 18 values will be sensor readings.
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # User clicked close button
            running = False
    inputData = serialport.readline().decode('ascii') # Read from serial
    inputData = inputData.replace("\r\n","") # Remove special characters
    
    if inputData != 'N': # If the value read from serial is not an N, that means it is a valid sensor reading, and should be appended to the sensor reading list.
        inputData = float(inputData) * 4.3 / 4096 #Convert binary reading to values that the model was trained on.
        
        # If sensor processed value is larger than expected max value, keep value at max value
        if inputData >= max_value:
            inputData = max_value
        inputList.append(inputData)
      
      
      
    else: # If value read from serial is an N, that means that a batch of 18 sensor values were sent out.
    
        inputList = switcharoo(inputList) # rearrangement of input data
        xTest = pd.DataFrame(data=[inputList], columns=['1','2','3','4']) # Send all sensor readings in the list to a dataframe

        # print(xTest)
        arr2d = np.reshape(inputList,(2,2))

        if np.all(arr2d==0):
            arr2d.fill(0.001)

        #print(arr2d)

        for row in range(2):
            for col in range(2):
                # green_value = int(arr2d[row][col]*255/np.max(arr2d))
                green_value = int(arr2d[row][col]*255/max_value)
                square_color = (0, green_value, 0)
                pygame.draw.rect(screen, square_color, pygame.Rect(col * square_size, row * square_size, square_size, square_size))
                # pygame.draw.rect(screen, quit_button_color, quit_button_rect)
        font = pygame.font.Font(None, 36)
        # text = font.render("Quit", True, (255, 255, 255))
        # screen.blit(text, (screen_size[0] // 2 - 30, screen_size[1] - 40))       
        
        pygame.display.flip()
        inputList.clear()


# print("Accuracy: ", metrics.accuracy_score(yValidationDf,y_pred))
# print(y_pred)
pygame.quit()