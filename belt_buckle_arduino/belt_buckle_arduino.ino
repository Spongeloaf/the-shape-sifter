#include "bb_parameters.h"
#include "EventDriver.h"



// declare all primary control interfaces in the global scope so everyone can use them.
BinController			bins{};
ArrayPrint				aprint{};
PartTracker				parts{};
FeederController		feeder{};
BeltController			belt{};
EncoderController		encoder{};
EventDriver				events{};
SerialPacket			packet{};



void setup() {
																			
	//  TODO: add version number transmission as a separate bytes array. Also add version number to handshake command
	Serial.begin(57600);
	Serial.print("[BB_ONLINE]");
	
	// Wait for server.
	delay(100);
	Serial.print("[Belt Buckle v0.6.2]");			
	encoder.init();														
}


void loop() {

	events.read_serial_port();

	events.check_inputs();

	events.check_distances();

	events.check_feeder();

	events.check_encoder();
	
	events.check_airjets();
}

