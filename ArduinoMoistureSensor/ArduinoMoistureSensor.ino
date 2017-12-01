#include "LowPower.h"
#include <SoftwareSerial.h>
SoftwareSerial BTSerial = SoftwareSerial(10, 11); // RX | TX
int sensor_pin = A0; 
int output_value;
char data[20];
int sleepTime;
String typeSleep;
bool sleepOrNot;
String toPrint;
String len;


void setup() {
  Serial.begin(115200);
  delay(2000);
  randomSeed(3);
  }
  
void sleepSeconds(int sleepTimer){
  int countDown = sleepTimer/8;
  for(int j = 0; j<countDown; j++){
    LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
    }
}

bool compareDataRx(){
  if (strcmp(data, "") != 0){
    Serial.println(data);
    return true;
  }
  return false;
}

void emptyData(){
  for (int x=0;x<20;x++){
    data[x] = '\0';
  }
}

void retrieveDataRx() {
  emptyData();
  if(Serial.available()) {
    Serial.readBytes(data,20);  // retrieve the 20 characters max received
    Serial.println(data);
    
  }
}

String padWithZero(String toPad, int numToPad){
  while(toPad.length() < numToPad){
    toPad = "0"+toPad;
  }
  return toPad;
}

int numDigits(int number){
  int digits = 0;
  if(number == 0) return 1;
  if(number < 0 ) digits = 1;
  while(number){
    number = number/10;
    digits ++;
  }
  return digits;
}


void loop() {
  //Serial.flush();
      output_value = -1;
      for(int i = 0; i < 25; i++){
        output_value = analogRead(sensor_pin);
        if(output_value != -1 || output_value != 0){ 
          break;
         }
        delay(50);
      }

      
      len = padWithZero(String(numDigits(output_value)),3);
      toPrint = String("s") + len + output_value;
      sleepTime = 1800;

      toPrint = toPrint+toPrint+toPrint+toPrint;
      for(int i = 0; i < 200; i ++){
        Serial.println(toPrint);
        delay(100);
        retrieveDataRx();
        sleepOrNot = compareDataRx();
        delay(100);
        if(sleepOrNot){
          sleepTime = 1800;
          break;
        }
      }
      
      typeSleep = sleepOrNot ? "LONG SLEEP" : "SHORT SLEEP";
      Serial.println(typeSleep);
      delay(100);
      //sleepSeconds(sleepTime);
}


