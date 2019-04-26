//Belt Encoder v0.7
//This lil' guy reads from the encoder and writes it to the belt buckle


#include <Wire.h>
#include <Encoder.h>

// Change these two numbers to the pins connected to your encoder.
//   Best Performance: both pins have interrupt capability
//   Good Performance: only the first pin has interrupt capability
//   Low Performance:  neither pin has interrupt capability
//   avoid using pins with LEDs attached
Encoder myEnc(3, 4);

unsigned long oldPosition  = 0;
unsigned long newPosition = 0;

void setup() {
  Wire.begin(2);                // join i2c bus with address #8
  Wire.onRequest(request_encoder); // register event
  //Serial.begin(19200);  // start serial for output
  //Serial.print("Belt Encoder v0.7");  
}

void loop() {
  newPosition = myEnc.read();
  //Serial.println(newPosition);
  //delay(100); 
}


// function that executes whenever data is requested by master
// this function is registered as an event, see setup()
void request_encoder()
{
byte myArray[4];

myArray[0] = (newPosition >> 24) & 0xFF;
myArray[1] = (newPosition >> 16) & 0xFF;
myArray[2] = (newPosition >>  8) & 0xFF;
myArray[3] = newPosition & 0xFF;
 
Wire.write(myArray, 4);
}


 
