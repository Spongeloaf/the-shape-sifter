/*
 * bb_parameters.h
 *
 * Created: 4/25/2019 11:20:03 PM
 *  Author: spongeloaf
 */ 



#ifndef BB_PARAMETERS_H_
#define BB_PARAMETERS_H_


// Global parameters used by almost all classes.
namespace gp {	
	
	// These globals are used for setting up pin numbers, and size parameters.
	// They are all magic constants that may change. All of them are used in constructing the main controller objects.
	// Magic constants which are unlikely to change exist within each class's constructor.
	constexpr int feeder_start_pin = 2;						// Startup control pin of the hopper.
	constexpr int feeder_pwm_pin = 3;						// PWM pin number of the hopper. Should be 3.
	constexpr int belt_control_pin = 52;					// Pin connected to belt drive relay.
	constexpr int wire_address = 2;							// I2C address of the belt encoder. This is the address we read from.
	constexpr int part_list_length = 64;                    // the number of parts we can keep track of - global
	constexpr int num_inputs = 8;							// self explanatory, I hope
	constexpr unsigned long debounce_delay = 210;           // the input debounce time
	constexpr int number_of_bins = 16;
	constexpr int print_size = 64;							// max array size to print. Increasing it will consume more memory.
	unsigned long sim_scaler = 1;							// scales the output of millis() for use in the packet sim. See trello for details.
	constexpr unsigned int feeder_delay = 750;				// milliseconds to wait before starting the feeder.
	constexpr unsigned long distance_offset = 1000;

	// These cannot be changed without modifying the packet structure and parts of event driver.
	// They are used in the parsing of packets.
	// DO NOT CHANGE THEM UNLESS YOU KNOW EXACTLY WHAT YOU ARE DOING!
	constexpr int packet_length = 23;						// length in bytes of each command packet
	constexpr int csum_length = 5;							// length in bytes of of the CSUM +1 for terminator
	constexpr int argument_length = 5;						// number of bytes in the packet argument
	constexpr int payload_length = 13;						// number of bytes in the packet payload
	constexpr int serial_str_len = 24;						// length in bytes of a packet string plus null terminator.
}


// a struct to hold packet data
struct SerialPacket {
	char raw_default[gp::packet_length + 1] = { '<','z','Z','Z','Z','z','z','z','z','z','z','z','z','z','z','z','z','z','C','S','U','M','>','\0' };
	char raw_packet[gp::packet_length + 1] = { '<','z','Z','Z','Z','z','z','z','z','z','z','z','z','z','z','z','z','z','C','S','U','M','>','\0' };
	char command = 'z';
	unsigned int argument_int = 0;                               // int to store the packet argument
	char argument_arr[gp::argument_length] = { 'z' };            // char array for parsing packet arguments
	char payload[gp::payload_length] = { 'z' };                  // char array for parsing packet payload
	signed long payload_int = -1;								 // and integer version of the payload, converted by atoi(). -1 is default because most values used by this will be 0 or positive.
	int result = 408;											 // Error messages are a letter designator matching the command, followed by a three digit number. Default is 408 "Status not set"
};


// holds one part in the part_list
struct TrackedPart {
	
bool occupied = false;				// false == this slot is available for use by a new part.
bool assigned = false;				// false == part has not been assigned to a bin
unsigned int bin = 0;				// destination bin, zero by default
unsigned long distance = 0;			// belt encoder reading at the time of part being added.
char id[gp::payload_length] = {'z','z','z','z','z','z','z','z','z','z','z','z','\0'};
};



#endif /* BB_PARAMETERS */