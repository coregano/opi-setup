// This script sends 4 sensor readings over serial. Meant for posture analyzer with 4 sensors at butt
#include <bluefruit.h>

#define adcButt A1 // The analog pin we use to read the 4 butt sensors

#define counterBit0 5// pin of First bit of the mux counter
#define counterBit1 6// pin of Second bit of the mux counter
#define counterBit2 9// pin of Third bit of the mux counter
#define counterBit3 10// pin of Fourth bit of the mux counter

#define waitTime 20

uint8_t counterPins[4] = {counterBit0, counterBit1, counterBit2, counterBit3};

uint16_t buttReadings[4] = {0, 0, 0, 0}; // caches back readings

void setup() {
  // put your setup code here, to run once:
  pinMode(counterBit0, OUTPUT); // Pinmode declaration
  pinMode(counterBit1, OUTPUT); // Pinmode declaration
  pinMode(counterBit2, OUTPUT); // Pinmode declaration
  pinMode(counterBit3, OUTPUT); // Pinmode declaration

  Serial.begin(9600);
  Serial.println("Serial started!");

}

void loop() {
  // put your main code here, to run repeatedly:
  ReadAllSensors();
  SendAllSensorData();
}

void ReadAllSensors() // Reads all sensors
{
  for (int i = 0; i < 4; i++) // loops through 9 times, each time it reads from one butt sensor and one back sensor
  {
    SetBitPins(i); // sets the 4 bit pins that controls the mux
    buttReadings[i] = analogRead(adcButt); // reads and saves the sensor reading
    delay(waitTime);
  }
}

void SetBitPins(uint8_t counterNumber) //Sets the 4 mux controller pins to the binary representation of the number that is input into this method
{
  int pinState = 0; // caches the state of the pin
  for (int i = 0; i < 4; i++)
  {
    pinState = bitRead(counterNumber, i); // Extracts the bit at position i from counterNumber
    digitalWrite(counterPins[i], pinState); // takes the MUX counter pin and sets the pin state
  }
}

void SendAllSensorData() // packages the buttReadings array and backReadings array into a single array and sends it over bluetooth
{
  for (int i = 0 ; i < 4; i++)
  {
    //Serial.print(i+1);
    //Serial.print(": ");
    Serial.println(buttReadings[i]);
    delay(waitTime);
  }
  Serial.println("N");
  delay(100);
}
