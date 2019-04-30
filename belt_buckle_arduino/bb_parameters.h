/*
 * bb_parameters.h
 *
 * Created: 4/25/2019 11:20:03 PM
 *  Author: spongeloaf
 */ 



#ifndef BB_PARAMETERS_H_
#define BB_PARAMETERS_H_



// These globals are used for setting up pin numbers, and size parameters.
// They are all magic constants that may change. All of them are used in constructing the main controller objects.
// Magic constants which are unlikely to change exist within each class's constructor.
constexpr int hopper_pwm_pin = 3;						// PWM pin number of the hopper. Should be 3.
constexpr int belt_control_pin = 52;					// Pin connected to belt drive relay.
constexpr int wire_address = 2;							// I2C address of the belt encoder.
constexpr int index_length = 48;                        // the number of parts we can keep track of - global
constexpr int num_inputs = 8;							// self explanatory, I hope
constexpr unsigned long debounce_delay = 210;           // the input debounce time
constexpr int number_of_bins = 16;
constexpr int print_size;								// max array size to print. Increasing it will consume more memory.

// These cannot be changed without modifying the Server Interface class.
// They are used in the parsing of packets.
// DO NOT CHANGE THEM UNLESS YOU KNOW EXACTLY WHAT YOU ARE DOING!
constexpr int packet_length = 23;						// length in bytes of each command packet
constexpr int csum_length = 5;							// length in bytes of of the CSUM +1 for terminator
constexpr int argument_length = 5;						// number of bytes in the packet argument
constexpr int payload_length = 13;						// number of bytes in the packet payload
constexpr int serial_str_len = 24;				// length in bytes of a packet string plus null terminator.



// a struct to hold packet data
struct SerialPacket{
	char raw_default[packet_length + 1] =  {'<','z','z','z','z','z','z','z','z','z','z','z','z','z','z','z','z','z','C','S','U','M','>','\0'};
	char raw_packet[packet_length + 1] = {'<','z','z','z','z','z','z','z','z','z','z','z','z','z','z','z','z','z','C','S','U','M','>','\0'};
	char command = 'z';
	unsigned int argument_int = 0;                               // int to store the packet argument
	char argument_arr[argument_length] = {'z'};                  // char array for parsing packet arguments
	char payload[payload_length] = {'z'};                        // char array for parsing packet payload
	int result = 408;											 // Error messages are a letter designator matching the command, followed by a three digit number. Default is 408 "Status not set"
};



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


constexpr int input_pins[num_inputs] = {			// storing the pin numbers in an array is clever.
	4,								//  stick_up
	5,								//  stick_down
	6,								//  stick_left
	7,								//  stick_right
	8,								//  button_run
	9,								//  button_stop
	10,								//  button_belt,
	11								//  button_feeder,
};


bool input_active[num_inputs];				// stores the current state of each input - global


#endif /* BB_PARAMETERS */