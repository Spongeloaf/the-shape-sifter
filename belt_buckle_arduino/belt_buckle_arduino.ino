#include "bb_parameters.h"
#include "EventDriver.h"



// declare all primary control interfaces in the global scope so everyone can use them.
BinController		bins{};
ArrayPrint			aprint{};
PartTracker			parts{};
FeederController	feeder{};
BeltController		belt{};
EncoderController	encoder{};
EventDriver			events{};
SerialPacket		packet{};

unsigned long count = 0;
int loops = 0;

void setup() {
																			
	//  TODO: add version number transmission as a separate bytes array. Also add version number to handshake command
	Serial.begin(57600);
	Serial.print("[BB_ONLINE]");
	delay(100);										// This delay is to allow our serial read to timeout on the server.
	Serial.print("[Belt Buckle v0.5.9]");			//  display program name on boot
}


void loop() {

	events.read_serial_port();

	events.check_inputs();

	events.check_distances();
	
	events.check_encoder();
	
	events.check_feeder();
	
	if (count > 100000)
	{
		count = 0;
		loops++;
		Serial.print(loops);
		Serial.print(" x 100k loops: ");
		Serial.print(millis());
		Serial.println("ms");
	}	
	count++;
}

