#include "bb_parameters.h"
#include "FeederController.h"
#include "BinController.h"
#include "BeltController.h"
#include "ArrayPrint.h"
#include "PartTracker.h"
#include "EventDriver.h"
#include "EncoderController.h"
#include "ServerInterface.h"



// declare all primary control interfaces in the global scope so everyone can use them.
BinController bins{};
ArrayPrint aprint{};
PartTracker parts{};
FeederController feeder{hopper_pwm_pin};
BeltController belt{belt_control_pin};
EncoderController encoder{wire_address};
ServerInterface server{payload_length, csum_length, argument_length, packet_length};
EventDriver events{number_of_inputs, debounce_delay};
SerialPacket serial_packet{};



// needs to be moved into event driver or input controller.
//  input name enum for readability
enum input_enum {                                                
	stick_up,
	stick_down,
	stick_left,
	stick_right,
	button_run,
	button_stop,
	button_belt,
	button_feeder
};



void setup() {
																			
	//  TODO: add version number transmission as a separate bytes array. Also add version number to handshake command
	Serial.begin(57600);
	Serial.print("[BB_ONLINE]");
	delay(100);										// This delay is to allow our serial read to timeout on the server.
	Serial.print("[Belt Buckle v0.5.8]");			//  display program name on boot
}


void loop() {

	server.read_serial_port();
	
	events.check_inputs();

	events.check_distances();
	
	events.check_encoder();
}

