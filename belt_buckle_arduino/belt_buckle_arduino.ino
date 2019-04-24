#include "FeederController.h"
#include "BinController.h"
#include "BeltController.h"
#include "ArrayPrint.h"
#include "PartTracker.h"



// function prototypes
void send_ack(char, int, char (*));
void read_serial_port(void);
void parse_packet(char (*));
void check_inputs(void);
void event_tick();



// These globals are used for setting up pin numbers, and size parameters.
// Bin pin numbers are in bins.h, for readability and because they are the least likely to change.
const uint8_t hopper_pwm_pin = 3;						// PWM pin number of the hopper. Should be 3.
const uint8_t belt_control_pin = 52;					// Pin connected to belt drive relay.
const uint8_t wire_address = 2;							// I2C address of the belt encoder.
const uint8_t index_length = 48;                        // the number of parts we can keep track of - global
const uint8_t packet_length = 23;						// length in bytes of each command packet
const uint8_t csum_length = 5;							// length in bytes of of the CSUM +1 for terminator
const uint8_t argument_length = 5;						// number of bytes in the packet argument
const uint8_t payload_length = 13;						// number of bytes in the packet payload



// declare all primary control interfaces in the global scope so everyone can use them.
PartTracker parts{index_length, payload_length};
FeederController feeder{hopper_pwm_pin};
BeltController belt{belt_control_pin};
EncoderController encoder{wire_address};
BinController bins{};
ArrayPrint aprint{};



// ---- ALL GLOBALS IN THIS LIST MUST BE FACTORED OUT! --------- //
// We inititialize all of our local vars at the start of their functions; never in-line. It's much easier to track them. the only exceptions are vars used in for loops.
// Vars for loops or short term use vars may have single letter names like i. All other vars need verbose names.
const int number_of_inputs = 8;                                      // self explanatory, I hope - global
const unsigned long rollover_distance = 4294967295;									 // max int value to rollover from when checking distances
const unsigned long debounceDelay = 210;                             // the debounce time; increase if the output flickers 
unsigned long lastDebounceTime = 0;                                  // for de-bouncing
bool input_active[number_of_inputs];                                 // stores the current state of each input - global
bool input_previous_state = true;                                    // default to true because pull up resistors invert our logic
int  serial_read_string_index = 0;                                   // the current index number of the read string
char serial_read_string[packet_length + 1];                          // stores the read chars


enum input_enum {                                                    //  input name enum for readability
  stick_up,
  stick_down,
  stick_left,
  stick_right,
	button_run,
	button_stop,
	button_belt,
	button_feeder
};

const int input_pins[number_of_inputs] = {                                 // storing the pin numbers in an array is clever.
	4,					//  stick_up
	5,					//  stick_down           
  6,					//  stick_left           
  7,					//  stick_right           
  8,					//  button_run           
  9,					//  button_stop 					 
	10,					//  button_belt,					 
	11					//  button_feeder,					 
};						 


void setup() {
																			
	for (int i = 0; i < number_of_inputs; i++)	// setup our pins using a loop, makes it easier to add new pins
	{
		pinMode (input_pins[i], INPUT_PULLUP);
		input_active[i] = true;						// Remember that using internal pull-up resistors causes our true/false to be inverted!
	}

	//  TODO: add version number transmission as a separate bytes array. Also add version number to handshake command
	Serial.begin(57600);
	Serial.print("[BB_ONLINE]");
	delay(100);															  // This delay is to allow our serial read to timeout on the server.
	Serial.print("[Belt Buckle v0.5.8]");																											//  display program name on boot
}


void loop() {

	read_serial_port();
	
	check_inputs();

	event_tick();
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

 
void check_inputs(){                                                                // check the state of all inputs

  for (int i = 0; i < number_of_inputs; i++)                         // loop through the array of inputs
    {
      input_previous_state = input_active[i];                           // take the value from the previous loop and store it here
      input_active[i] = digitalRead(input_pins[i]);                           // read the current input state
  
      if (input_active[i] == false) {                                   // false here means input is active because of pull-up resistors!
        {
          if (input_active[i] != input_previous_state)                  // checks if the state changed from our last trip through the loop
          {
            if ((millis() - lastDebounceTime) > debounceDelay)          // We use the number of milliseconds the arduino has been running for to see if it's been more than X number of millis since we last pressed a input It doesn't necessarily stop all input bouncing, but it helps. 
            {
              lastDebounceTime = millis();                              // reset the debounce timer.
              switch (i)                                                // take action if a input is pressed.
              {
                case stick_up:
					feeder.speed_up();
					Serial.print("speed: ");
					Serial.println(feeder.get_speed());                           
					break;
  
                case stick_down:
					feeder.speed_down();
					Serial.print("speed: ");
					Serial.println(feeder.get_speed());                      
					break;
  
                case stick_left:
					belt.toggle_mode();
					Serial.print("belt is: ");                         // replace this with a usable action at some point
					Serial.println(belt.get_mode());
					break;
  
                case stick_right:
					feeder.toggle();
					Serial.print("Mode: ");
					Serial.print(feeder.get_mode());
					Serial.print(" Speed: ");
					Serial.println(feeder.get_speed());                         // replace this with a usable action at some point
					break;

				case button_run:
					Serial.println("button_run");                         // replace this with a usable action at some point
					break;

				case button_stop:
					Serial.println("button_stop");                        // replace this with a usable action at some point
					break;

				case button_belt:
					Serial.println("button_belt");                         // replace this with a usable action at some point
					break;

				case button_feeder:
					Serial.println("button_feeder");                         // replace this with a usable action at some point
					break;


              }
            }
          }
        }
      }
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


void event_tick()
{
	// There's a bit of non-conventionality in here. 
	// Because we are working with meat-space machinery, we need to wait and continually check on certain procedures.
	// this includes things like turning air jets off after a few milliseconds, and waiting for feeder startup phases.
	
	unsigned long dist = encoder.get_dist();
	bins.check_distances(dist);

	if (feeder.get_startup())
	{
		feeder.start();
	}
	
}

