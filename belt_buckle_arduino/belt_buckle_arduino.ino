#include "FeederController.h"
#include "BinController.h"
#include "BeltController.h"
#include "ArrayPrint.h"
#include "PartTracker.h"



// function prototypes
void send_ack(char, int, char (*));
void read_serial_port(void);
void parse_packet(char (*));




// These globals are used for setting up pin numbers, and size parameters.
// Bin pin numbers are in bins.h, for readability and because they are the least likely to change.
const int hopper_pwm_pin = 3;						// PWM pin number of the hopper. Should be 3.
const int belt_control_pin = 52;					// Pin connected to belt drive relay.
const int wire_address = 2;							// I2C address of the belt encoder.
const int index_length = 48;                        // the number of parts we can keep track of - global
const int packet_length = 23;						// length in bytes of each command packet
const int csum_length = 5;							// length in bytes of of the CSUM +1 for terminator
const int argument_length = 5;						// number of bytes in the packet argument
const int payload_length = 13;						// number of bytes in the packet payload
const int number_of_inputs = 8;                     // self explanatory, I hope
const unsigned long debounce_delay = 210;            // the input debounce time



// declare all primary control interfaces in the global scope so everyone can use them.
PartTracker parts{index_length, payload_length};
FeederController feeder{hopper_pwm_pin};
BeltController belt{belt_control_pin};
EncoderController encoder{wire_address};
BinController bins{};
ArrayPrint aprint{};
EventDriver events{number_of_inputs, debounce_delay};



// ---- ALL GLOBALS IN THIS LIST MUST BE FACTORED OUT! --------- //
// We inititialize all of our local vars at the start of their functions; never in-line. It's much easier to track them. the only exceptions are vars used in for loops.
// Vars for loops or short term use vars may have single letter names like i. All other vars need verbose names.
const unsigned long rollover_distance = 4294967295;									 // max int value to rollover from when checking distances
int  serial_read_string_index = 0;                                   // the current index number of the read string
char serial_read_string[packet_length + 1];                          // stores the read chars



void setup() {
																			
	//  TODO: add version number transmission as a separate bytes array. Also add version number to handshake command
	Serial.begin(57600);
	Serial.print("[BB_ONLINE]");
	delay(100);										// This delay is to allow our serial read to timeout on the server.
	Serial.print("[Belt Buckle v0.5.8]");			//  display program name on boot
}


void loop() {

	read_serial_port();
	
	events.check_inputs();

	events.check_distances();
	
	events.check_encoder();
}


void read_serial_port(){

  // We inititialize all of our local vars here; never in-line. It's much easier to track them. the only exceptions are vars used in for loops.
  char serial_char;
  if (Serial.available() > 0)
    {
    serial_char = Serial.read();                                        //  Read a character
    // print_array(serial_read_string);                                  // for debugging

    switch (serial_char) 
      {
      case '<':                                                         // '<' is the packet initiator.
        memset(&serial_read_string[0], 0, sizeof(serial_read_string));  // clear the array every time we get a new initiator.
        serial_read_string_index = 0;                                   // reset the array index because we're starting a new command.
        serial_read_string[0] = serial_char;                            // place our '<' character at the beginning of the array
        serial_read_string_index = serial_read_string_index + 1;        // increment array index number
        
        // print_array(serial_read_string);                              // for debugging
        // Serial.println("packet initiator found");                     // for debugging
      break;
      
      case '>':                                                         // '>' is the packet terminator.
        serial_read_string[serial_read_string_index] = serial_char;     // add the terminator to the string before we begin
				parse_packet(serial_read_string);                               // executes the received packet
        memset(&serial_read_string[0], 0, sizeof(serial_read_string));  // clear the array every time we get a new initiator.
        serial_read_string_index = 0;                                   // reset the packet array index to 0
        
        // Serial.println(strlen(serial_read_string));                   // for debugging
        // print_array(serial_read_string);                              // for debugging
        // Serial.println("packet terminator found");                    // for debugging       
      break;
      
      default:
        if (serial_read_string_index < (sizeof(serial_read_string) - 2))          // if the serial read string get too long, we stop adding to it to prevent overruns.
          {
            serial_read_string[serial_read_string_index] = serial_char;     // append the read character to the array
            serial_read_string_index = serial_read_string_index + 1;        // increment the array index number 
          }
        else                                                            // should we receive more than 22 characters before a terminator, something is wrong, dump the string.
        {
        memset(&serial_read_string[0], 0, sizeof(serial_read_string));  // clear the array every time we get a new initiator.
        serial_read_string_index = 0;                                   // reset the array index because we're starting a new command.
        }
      }
      
    }
}


void parse_packet(char packet[]){																					// parses the command and then passes the relevant data off to wherever it needs to go. 

unsigned int parse_packet_argument_int = 0;                               // int to store the packet argument
char parse_packet_argument_arr[argument_length];                          // char array for parsing packet arguments
char parse_packet_payload[payload_length];                                // char array for parsing packet payload 
int parse_command_result = 0;																							// Error messages are a letter designator matching the command, followed by a three digit number

  // ------------TODO: Needs to have CSUM installed HERE------------
  
  // Serial.print("Packet length:");                                       // for debugging
  // Serial.println(strlen(packet));                                       // for debugging
  
  if (strlen(packet) == packet_length)																		// this is a really basic packet check. We need a better one.
    {
      
      // Serial.println("Parsing packet : Length OK");											// for debugging
     
      //  this loop sets up the argument array
      for (int i = 0; i <= argument_length - 2; i++)                      // argument length -2, because the last character is \0 and we are zero indexed 
        {
          parse_packet_argument_arr[i] = packet[i + 2];                   //  the argument begins on the [2] char
        }
      parse_packet_argument_arr[4] = '\0';                                // don't forget the terminator on the array!
      parse_packet_argument_int = atoi(parse_packet_argument_arr);        // the bin number is more useful as an int than an array. But now we have both.

      //  this loop sets up the payload array
      for (int i = 0; i <= payload_length - 2; i++)                       // payload length -2, because the last character is \0 and we are zero indexed
        {
          parse_packet_payload[i] = packet[i + 6];                        //  the argument begins on the [2] char
        }
      parse_packet_payload[payload_length - 1] = '\0';   
			

          
      // switch case for all the different command types.
      // see trello for a list of commands
      switch (packet[1])
      {
        case 'A':
			// Add a new part instance
			parse_command_result = add_part(parse_packet_payload);
			send_ack(packet[1], parse_command_result, parse_packet_payload);
			break;
          
        case 'B':
			// assign a bin number
			parse_command_result = assign_bin(parse_packet_argument_int, parse_packet_payload);
			send_ack(packet[1], parse_command_result, parse_packet_payload);
			break;
          
		case 'G':
			// print current distance
			Serial.println(encoder.get_dist());
		break;
		  
        case 'H':
			// handshake
			Serial.print("Command ");
			Serial.print(packet[1]);
			Serial.println(" Received");
        break;

        case 'O':
			// flush index
			flush_part_array(parse_packet_argument_int);
			send_ack(packet[1], parse_command_result, parse_packet_payload);
        break;

        case 'X':
			// print part index
			aprint.array_2d(index_payload);
			break;

        case 'P':
			// print part index with bins and distance
			aprint.part_index_full();
			break;

        case 'S':
			// print part index
			aprint.part_index_single(parse_packet_argument_int);
			break;
				
        case 'T':
			// test cycle the outputs, argument is time in ms for each pulse
			bins.test_outputs(parse_packet_argument_int);
			break;
				
		case 'W':
			//  analogWrite(hopper_pwm_pin, parse_packet_argument_int);
			break;

				}
    }
  else
    {
      Serial.print("Parsing packet : Bad Packet Length. Expected ");
      Serial.print(packet_length);
      Serial.print(" but received ");
      Serial.println(strlen(packet));                   
    }

}


void send_ack(char send_command, int send_command_result, char send_packet_payload[]){
	Serial.print("[ACK-");
	Serial.print(send_command);
	Serial.print("-");
	Serial.print(send_command_result);
	Serial.print("-");
	Serial.print(send_packet_payload);
	Serial.print("-");
	Serial.print("CSUM");
	Serial.print("]");
}

