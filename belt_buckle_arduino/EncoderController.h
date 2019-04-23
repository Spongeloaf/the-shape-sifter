#include <Wire.h>


class EncoderController{
public:
	
	EncoderController(int adr) 
	{
		Wire.begin();
		address = adr;
		bytes_len = 4;
	}
	
	unsigned long get_dist();
	
private:
	int address;
	int bytes_len;
};


// get the distance from the encoder. Credit: https:// thewanderingengineer.com/2015/05/06/sending-16-bit-and-32-bit-numbers-with-arduino-i2c/
unsigned long EncoderController::get_dist()																											
{
	unsigned long distance;
	byte a,b,c,d;

	Wire.requestFrom(address, bytes_len);																						
	if (Wire.available() > 0)
	{
		a = Wire.read();
		b = Wire.read();
		c = Wire.read();
		d = Wire.read();

		// bit shifting our four individual bytes into one unsigned long int
		distance = a;
		distance = (distance << 8) | b;
		distance = (distance << 8) | c;
		distance = (distance << 8) | d;

		return distance;
	}
	return 1;
}