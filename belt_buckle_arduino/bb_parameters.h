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
constexpr int number_of_inputs = 8;                     // self explanatory, I hope
constexpr unsigned long debounce_delay = 210;            // the input debounce time



// These cannot be changed without modifying the ServerInterface class.
// They are used in the parsing of packets.
// DO NOT CHANGE THEM UNLESS YOU KNOW EXACTLY WHAT YOU ARE DOING!
constexpr int packet_length = 23;						// length in bytes of each command packet
constexpr int csum_length = 5;							// length in bytes of of the CSUM +1 for terminator
constexpr int argument_length = 5;						// number of bytes in the packet argument
constexpr int payload_length = 13;						// number of bytes in the packet payload
constexpr int serial_read_string_len = 24;				// length in bytes of a packet string plus null terminator.



// a struct to hold packet data
struct SerialPacket{
	char raw_default[packet_length] =  {'<','z','z','z','z','z','z','z','z','z','z','z','z','z','z','z','z','z','C','S','U','M','>'};
	char raw_packet[packet_length] = {'<','z','z','z','z','z','z','z','z','z','z','z','z','z','z','z','z','z','C','S','U','M','>'};
	char command = 'z';
	unsigned int argument_int = 0;                               // int to store the packet argument
	char argument_arr[argument_length] = {'z'};                  // char array for parsing packet arguments
	char payload[payload_length] = {'z'};                        // char array for parsing packet payload
	int result = 0;												 // Error messages are a letter designator matching the command, followed by a three digit number
};



#endif /* BB_PARAMETERS */