#include <Wire.h>


// function prototypes
void send_ack(char, int, char (*));
void read_serial_port(void);
void print_array(char (*));
void print_array(unsigned long (*));
void print_array_2d( const char (*));
void print_part_index_full(void);
void print_part_index_single(int);
void parse_packet(char (*));
void check_inputs(void);
int add_part(char (*));
int assign_bin(int, char (*));
int add_part_and_assign_bin(char (*), int, char (*));
unsigned long get_distance_from_encoder(void);
void check_part_distances(void);
void turn_off_airjets(void);
void test_outputs(int t);
void flush_part_array(int);
void feeder_speed_up();
void feeder_speed_down();
void feeder_toggle_mode();
void belt_toggle_mode();




// We inititialize all of our local vars at the start of their functions; never in-line. It's much easier to track them. the only exceptions are vars used in for loops.
// Vars for loops or short term use vars may have single letter names like i. All other vars need verbose names.
const int packet_length = 23;                                        // length in bytes of each command packet
const int csum_length = 5;                                           // length in bytes of of the csum +1 for terminator
const int argument_length = 5;                                       // used by the parser to get the number of bytes in the packet arguement
const int payload_length = 13;                                       // used by the parser to get the number of bytes in the packet payload
const int part_index_length = 10;                                    // the number of parts we can keep track of - global
const int print_size = 32;                                           // this is used by the print array function, sets the max size to print. Increasing it will consume more memory, so set only what you need
const int number_of_inputs = 8;                                      // self explanatory, I hope - global
const int distance_length = 5;                                       // length in bytes of distance; unsinged int is 4 + 1 for \0
const unsigned long rollover_distance = 4294967295;									 // max int value to rollover from when checking distances
const unsigned long bin_tolerance = 1500;														 // width in dist units of the air jet to blow the part off the belt
const int number_of_bins = 16;																			 // max number of bins we can put on one belt
const unsigned long bin_airjet_time = 200;													 // time in milliseconds that the air jet stays on
const uint8_t hopper_pwm_pin = 3;																		 // PWM pin number of the hopper. Should be 3.

unsigned int part_index_working = 0;                                 // the next available index for storing a part
unsigned long bin_distance_config[number_of_bins + 1];							 // array that stores distance ints for each bin location
unsigned long part_index_distance[part_index_length];                // the main distance index - global
unsigned long bin_airjet_array[number_of_bins];											 // for timing air blasts
int part_index_bin[part_index_length];                               // the main bin index - global
char part_index_payload[part_index_length][payload_length];          // the main part index - global

const unsigned long debounceDelay = 210;                             // the debounce time; increase if the output flickers 
unsigned long lastDebounceTime = 0;                                  // for debouncing
bool input_active[number_of_inputs];                                 // stores the current state of each input - global
bool input_previous_state = true;                                    // default to true because pull up resistors invert our logic

unsigned long belt_total_distance = 0;                               // distance traveled by the belt - global
int bin_count;																											 // number of bins currently stored

int  serial_read_string_index = 0;                                   // the current index number of the read string
char serial_read_string[packet_length + 1];                          // stores the read chars

int pwm_timer = 0;
int feeder_speed_selector = 0;																			 // selects the current feeder speed from the feeder_speed_array 
bool feeder_mode = false;																						 // bool to control the current speed of the belt, so we can turn it off wihtout changing speed.
const int feeder_num_speeds = 12;																		 // The number of speeds the feeder has. Used to unsure speed_selector doesn't go out of bounds. 
const int belt_control_pin = 52;																		 // conveyor belt on/off control HIGH is ON.
bool belt_mode = false;


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

const int pins[number_of_inputs] = {                                 // storing the pin numbers in an array is clever.
	4,					//  stick_up
	5,					//  stick_down           
  6,					//  stick_left           
  7,					//  stick_right           
  8,					//  button_run           
  9,					//  button_stop 					 
	10,					//  button_belt,					 
	11					//  button_feeder,					 
};						 

const int bins[number_of_bins + 1] = {                                    // storing the bin output pin numbers in an array is clever.
	0,
	22,
	23,
	24,
	25,
	26,
	27,
	28,
	29,
	30,
	31,
	32,
	33,
	34,
	35,
	36,
	37,
};

const int feeder_speed_array [feeder_num_speeds + 1] = {
20,
30,
40,
50,
60,
75,
100,
125,
150,
175,
200,
225,
255
};

void setup() {

	for (int i = 1; i <= number_of_bins; i++ )																	// setting up our bin outputs and writing values to LOW.
		{
			pinMode(bins[i], OUTPUT);
			digitalWrite(bins[i], LOW);
		}
																						
  for (int i = 0; i < number_of_inputs; i++)																	// setup our pins using a loop, makes it easier to add new pins
  {
    pinMode (pins[i], INPUT_PULLUP);
    input_active[i] = true;																									  // Remember that using internal pullup resistors causes our true/false to be inverted!
  }
	
	bin_distance_config[0] = 0;
	bin_distance_config[1] = 17508;
	bin_distance_config[2] = 20295;

	pinMode(belt_control_pin, OUTPUT);
	digitalWrite(belt_control_pin, LOW);
			
	Wire.begin();																																								//  join i2c bus (address optional for master)
	
	//  TODO: add version number transmission as a separate bytes array. Also add version number to handshake command
	Serial.begin(57600);
	Serial.print("[BB_ONLINE]");
	delay(100);															  // This delay is to allow our serial read to timeout on the server.
	Serial.print("[Belt Buckle v0.5.6]");																											//  display program name on boot
}

void loop() {

  read_serial_port();
	
  check_inputs();

	check_part_distances();

	turn_off_airjets();

}

void read_serial_port(){

  // We inititialize all of our local vars here; never in-line. It's much easier to track them. the only exceptions are vars used in for loops.
  char serial_char;
  if (Serial.available() > 0)
    {
    serial_char = Serial.read();                                        //  Read a character
    // print_array(serial_read_string);                                  // for debuggin'

    switch (serial_char) 
      {
      case '<':                                                         // '<' is the packet initiator.
        memset(&serial_read_string[0], 0, sizeof(serial_read_string));  // clear the array every time we get a new initiator.
        serial_read_string_index = 0;                                   // reset the array index because we're starting a new command.
        serial_read_string[0] = serial_char;                            // place our '<' character at the beginning of the array
        serial_read_string_index = serial_read_string_index + 1;        // increment array index number
        
        // print_array(serial_read_string);                              // for debuggin'
        // Serial.println("packet initiator found");                     // for debuggin'
      break;
      
      case '>':                                                         // '>' is the packet terminator.
        serial_read_string[serial_read_string_index] = serial_char;     // add the terminator to the string before we begin
				parse_packet(serial_read_string);                               // executes the received packet
        memset(&serial_read_string[0], 0, sizeof(serial_read_string));  // clear the array every time we get a new initiator.
        serial_read_string_index = 0;                                   // reset the packet array index to 0
        
        // Serial.println(strlen(serial_read_string));                   // for debuggin'
        // print_array(serial_read_string);                              // for debuggin'
        // Serial.println("packet terminator found");                    // for debuggin'        
      break;
      
      default:
        if (serial_read_string_index < (sizeof(serial_read_string) - 2))          // if the serial read string get too long, we stop adding to it to prevent overruns.
          {
            serial_read_string[serial_read_string_index] = serial_char;     // append the read character to the array
            serial_read_string_index = serial_read_string_index + 1;        // increment the array index number 
          }
        else                                                            // should we recieve more than 22 characters before a temrinator, something is wrong, dump the string.
        {
        memset(&serial_read_string[0], 0, sizeof(serial_read_string));  // clear the array every time we get a new initiator.
        serial_read_string_index = 0;                                   // reset the array index because we're starting a new command.
        }
      }
      
    }
}

void print_array(char to_be_printed[print_size]){                    // prints an array of characters
  for (int i = 0; i <= print_size; i++)
  {
    if (to_be_printed[i] == '\0')
    {
      Serial.print("\r\n");
      return;
    }
    Serial.print(to_be_printed[i]);
  }
}

void print_array(unsigned long to_be_printed[print_size]){                    // prints an array of characters
	for (int i = 0; i <= print_size; i++)
	{
		if (to_be_printed[i] == '\0')
		{
			Serial.print("\r\n");
			return;
		}
		Serial.print(to_be_printed[i]);
		Serial.print("\r\n");
	}
}

void print_array_2d( const char a[][ payload_length ] ) {
   
   for ( int i = 0; i < part_index_length; ++i ) {               //  loop through array's rows
      
      for ( int j = 0; j < payload_length; ++j ) 
        {                //  loop through columns of current row
          Serial.print (part_index_payload[ i ][ j ] );
        }  
    Serial.print ("\n") ; //  start new line of output
    } 
   
} 

void print_part_index_full() {
   
   Serial.println("  Payload    :  Dist. : Bin") ;    
   for ( int i = 0; i < part_index_length; ++i )                     //  loop through array's rows
      {
        
        for ( int j = 0; j < payload_length; ++j ) 
          {                //  loop through columns of current row
            Serial.print (part_index_payload[ i ][ j ] );
          }
            
        Serial.print(" : ") ;       
        Serial.print(part_index_distance[i]);
        Serial.print(" : ") ;    
        Serial.print(part_index_bin[i]);            
        Serial.print("\n") ; //  start new line of output
      } 
} 

void print_part_index_single(int i) {
   
   Serial.println("  Payload    :  Dist. : Bin") ;    
        
      for ( int j = 0; j < payload_length; ++j ) 
        {                //  loop through columns of current row
          Serial.print (part_index_payload[ i ][ j ] );
        }
          
      Serial.print(" : ") ;       
      Serial.print(part_index_distance[i]);
      Serial.print(" : ") ;    
      Serial.print(part_index_bin[i]);            
      Serial.print("\n") ; //  start new line of output
      
   
} 

void parse_packet(char packet[]){																					// parses the command and then passes the relevant data off to wherever it needs to go. 

unsigned int parse_packet_argument_int = 0;                               // int to store the packet argument
char parse_packet_argument_arr[argument_length];                          // char array for parsing packet arguments
char parse_packet_payload[payload_length];                                // char array for parsing packet payload 
int parse_command_result = 0;																							// Error messages are a letter designator matching the command, followed by a three digit number

  // ------------TODO: Needs to have CSUM installed HERE------------
  
  // Serial.print("Packet length:");                                       // for debuggin'
  // Serial.println(strlen(packet));                                       // for debuggin'
  
  if (strlen(packet) == packet_length)																		// this is a really basic packet check. We need a better one.
    {
      
      // Serial.println("Parsing packet : Length OK");											// for debuggin'
     
      //  this loop sets up the argument array
      for (int i = 0; i <= argument_length - 2; i++)                      // argument length -2, because the last character is \0 and we are zero indexed 
        {
          parse_packet_argument_arr[i] = packet[i + 2];                   //  the arguemnt begines on the [2] char
        }
      parse_packet_argument_arr[4] = '\0';                                // dont forget the terminator on the array!
      parse_packet_argument_int = atoi(parse_packet_argument_arr);        // the bin number is more useful as an int than an array. But now we have both.

      //  this loop sets up the payload array
      for (int i = 0; i <= payload_length - 2; i++)                       // payload length -2, because the last character is \0 and we are zero indexed
        {
          parse_packet_payload[i] = packet[i + 6];                        //  the arguemnt begines on the [2] char
        }
      parse_packet_payload[payload_length - 1] = '\0';   
			

          
      // switch case for all the differrent command types.
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
				Serial.println(get_distance_from_encoder());
			break;
		  
        case 'H':
          // handshake
          Serial.print("Command ");
          Serial.print(packet[1]);
          Serial.println(" Recieved");
        break;

        case 'O':
					// flush index
					flush_part_array(parse_packet_argument_int);
					send_ack(packet[1], parse_command_result, parse_packet_payload);
        break;

        case 'X':
          // print part index
          print_array_2d(part_index_payload);
          break;

        case 'P':
          // print part index with bins and distance
          print_part_index_full();
          break;

        case 'S':
          // print part index
          print_part_index_single(parse_packet_argument_int);
          break;
				
        case 'T':
					// test cycle the outputs, argument is time in ms for each pulse
					test_outputs(parse_packet_argument_int);
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
      Serial.print(" but recieved ");
      Serial.println(strlen(packet));                   
    }

}
 
void check_inputs(){                                                                // check the state of all inputs

  for (int i = 0; i < number_of_inputs; i++)                         // loop through the array of inputs
    {
      input_previous_state = input_active[i];                           // take the value from the previous loop and store it here
      input_active[i] = digitalRead(pins[i]);                           // read the current input state
  
      if (input_active[i] == false) {                                   // false here means input is active because of pullup resistors!
        {
          if (input_active[i] != input_previous_state)                  // checks if the state changed from our last trip through the loop
          {
            if ((millis() - lastDebounceTime) > debounceDelay)          // We use the number of milliseconds the arduino has been running for to see if it's been more than X number of millis since we last pressed a input It doesn't necessarily stop all input bouncing, but it helps. 
            {
              lastDebounceTime = millis();                              // reset the debounce timer.
              switch (i)                                                // take action if a input is pressed.
              {
                case stick_up:
									feeder_speed_up();
									Serial.print("speed: ");
                  Serial.println(feeder_speed_selector);                           // replace this with a usable action at some point
                  break;
  
                case stick_down:
									feeder_speed_down();
									Serial.print("speed: ");
                  Serial.println(feeder_speed_selector);                         // replace this with a usable action at some point
                  break;
  
                case stick_left:
									belt_toggle_mode();
                  Serial.print("belt is: ");                         // replace this with a usable action at some point
                  Serial.println(belt_mode);
									break;
  
                case stick_right:
									feeder_toggle_mode();
									Serial.print("Mode: ");
									Serial.print(feeder_mode);
									Serial.print(" Speed: ");
                  Serial.println(feeder_speed_selector);                         // replace this with a usable action at some point
									break;

                case button_run:
									Serial.println("button_run");                         // replace this with a usable action at some point
									break;

								case button_stop:
                  Serial.println("button_stop");                         // replace this with a usable action at some point
                  break;

								case button_belt:
									Serial.println("button_belt");                         // replace this with a usable action at some point
									break;

								case button_feeder:
									Serial.println("button_feeder");                         // replace this with a usable action at some point
									feeder_toggle_mode();
									break;


              }
            }
          }
        }
      }
    }
  }

int add_part(char packet_payload[]){                                                      // Adds a new part instance to the part index array
	
	bool valid_part = true;

  // first check to see if this part number exists already
    for (unsigned int i = 0; i < part_index_length; i++)
    {
	    if (memcmp(part_index_payload[i], packet_payload, payload_length) == 0)
	    {
			return 409;
		}
	}	
	
  for (int i = 0; i < payload_length; i++)                                          // Stores the recieved part index in the DB
  {                          
    part_index_payload[part_index_working][i] = packet_payload[i];
  }

  part_index_distance[part_index_working] = get_distance_from_encoder();                    // set the belt distance
  part_index_bin[part_index_working] = 0;                                           // bin is always 0 until the sort command
  part_index_working++;
  
  if (part_index_working >= part_index_length)                          
  {
    part_index_working = 0;
  }
  return 200;
}

int assign_bin(int packet_argument, char packet_payload[]){             // assign a part to a bin. loops through the payload array, returns 404 if the part isnt found

    for (unsigned int i = 0; i < part_index_length; i++)
    {
      if (memcmp(part_index_payload[i], packet_payload, payload_length) == 0)   // Reminder: memcmp returns 0 when it finds a match. 
        {            
            part_index_bin[i] = packet_argument;
            return 200;
        }
    }
		return 404;																														

}

int add_part_and_assign_bin(char packet_payload[], int assign_argument, char assign_payload[])
	{
			//  TODO: figure out what in gods name is wrong with the arguments here. l_payload? WTF. And is assign_payload even used?
			bool valid_part = true;

			// first check to see if this part number exists already
			for (unsigned int i = 0; i < part_index_length; i++)
			{
				if (memcmp(part_index_payload[i], packet_payload, payload_length) == 0)
				{
					return 409;
				}
			}
			
			for (int i = 0; i < payload_length; i++)                                          // Stores the received part index in the DB
			{
				part_index_payload[part_index_working][i] = packet_payload[i];
			}

			part_index_distance[part_index_working] = get_distance_from_encoder();                    // set the belt distance
			part_index_bin[part_index_working] = assign_argument;                                     // set the bin number
			part_index_working++;
			
			if (part_index_working >= part_index_length)
			{
				part_index_working = 0;
			}
			return 200;
	}

unsigned long get_distance_from_encoder()																											// get the distance from the encoder. Credit: https:// thewanderingengineer.com/2015/05/06/sending-16-bit-and-32-bit-numbers-with-arduino-i2c/
{																																	
	unsigned long distance;		
	byte a,b,c,d;

	Wire.requestFrom(2,4);																						// I2C device 2, read 4 bytes
	if (Wire.available() > 0)
		{
			a = Wire.read();
			b = Wire.read();
			c = Wire.read();
			d = Wire.read();

			distance = a;																											// bit shifting our four individual bytes into one unsigned long int
			distance = (distance << 8) | b;
			distance = (distance << 8) | c;
			distance = (distance << 8) | d;

			return distance;
		}
return 1;
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

void check_part_distances(void)																																//  NOT FINISHED YET!!!!!   something is borken!
{
	unsigned long current_distance;
	unsigned long travelled_distance;
	unsigned long previous_distance;
	int b;
	
	current_distance = get_distance_from_encoder();
	if (current_distance == previous_distance)
		{
			//  Serial.println("Warning: distance variables == 0. Belt may not be moving");
		}
	
	for (unsigned int i = 0; i < part_index_length; i++)																										// loop through the main part array and determine if the 
		{		
			if (part_index_bin[i] > 0)																																					// checks to prevent sorting unassigned parts
				{
					travelled_distance = current_distance - part_index_distance[i];																	// gets the distance travelled since we last checked
					if (travelled_distance < 0)																																			// evaluates true when the distance int rolls over, UNTESTED!
						{
							travelled_distance = rollover_distance - current_distance + part_index_distance[i];
						}
					b = part_index_bin[i];																																					// gets the bin number we are using right now
					
					if (travelled_distance >= bin_distance_config[b] && travelled_distance <= (bin_distance_config[b] + bin_tolerance))
						{
							bin_airjet_array[b] = millis();																															// stash the time that the airjet was turned on, we'll turn it off later in the airjet 
							digitalWrite(bins[b], HIGH);																																	
							flush_part_array(i);
						}
				}
		}
	previous_distance = current_distance;
}

void turn_off_airjets()
{
	for (int i = 0; i < number_of_bins; i++ )
		{
			if (millis() > (bin_airjet_array[i] + bin_airjet_time))
				{
					digitalWrite(bins[i], LOW);
					bin_airjet_array[i] = 0;
				}
		}	
}

void test_outputs(int t)
{
		Serial.println("Testing outputs...");
		for (int i = 1; i <= number_of_bins; i++ )							// setting up our bin outputs and writing values to HIGH.
		{
			digitalWrite(bins[i], HIGH);
			delay(t);
			digitalWrite(bins[i], LOW);
			delay(t);
			Serial.print("output: ");
			Serial.println(bins[i]);
		} 
		Serial.println("Test complete");
}

void flush_part_array(int index)
{
		// this function zeroes the part index array. 
		// If the index number passed is out of bounds, an error is primnted.
		// If the index number passed is -1, the whole array is flushed.
			

		if ((-1 < index) && (index < part_index_length))	// zeroes one index of the array
			{
					part_index_bin[index] = 0;																																			
					part_index_distance[index] = 0;
					part_index_payload[index][0] = '0';																															
					part_index_payload[index][1] = '0';
					part_index_payload[index][2] = '0';
					part_index_payload[index][3] = '0';
					part_index_payload[index][4] = '0';
					part_index_payload[index][5] = '0';
					part_index_payload[index][6] = '0';
					part_index_payload[index][7] = '0';
					part_index_payload[index][8] = '0';
					part_index_payload[index][9] = '0';
					part_index_payload[index][10] = '0';
					part_index_payload[index][11] = '0';
					part_index_payload[index][12] = '\0';
					return;
			}
			if (index == -1)   // zeroes the whole array
				{
					for (int i=0; i < part_index_length; i++)
						{
							part_index_bin[i] = 0;
							part_index_distance[i] = 0;
							part_index_payload[i][0] = '0';
							part_index_payload[i][1] = '0';
							part_index_payload[i][2] = '0';
							part_index_payload[i][3] = '0';
							part_index_payload[i][4] = '0';
							part_index_payload[i][5] = '0';
							part_index_payload[i][6] = '0';
							part_index_payload[i][7] = '0';
							part_index_payload[i][8] = '0';
							part_index_payload[i][9] = '0';
							part_index_payload[i][10] = '0';
							part_index_payload[i][11] = '0';
							part_index_payload[i][12] = '\0';
						}
				return;
			}
		Serial.println("Error: Flush index out of range!");		// nothing is zeroed if index is out of range!
	}

void feeder_speed_up() 
{
	// raises feeder speed unless already maxed. Does not turn on feeder.
	// TODO: Add packet notification to the server of current feed speed.

	feeder_speed_selector++;

	// true at max speed, prevents accessing speed array out of range
	if (feeder_speed_selector > feeder_num_speeds)
	{
		feeder_speed_selector = feeder_num_speeds;
	}

	// only writes to analog output if the feeder is currently running
	if (feeder_mode)
	{
		analogWrite(hopper_pwm_pin, feeder_speed_array[feeder_speed_selector]);
	}
}

void feeder_speed_down()
{
	// raises feeder speed unless already maxed. Does not turn on feeder.
	// TODO: Add packet notification to the server of current feed speed.

	feeder_speed_selector--;

	// true at max speed, prevents accessing speed array out of range
	if (feeder_speed_selector < 0)
	{
		feeder_speed_selector = 0;
	}

	// only writes to analog output if the feeder is currently running
	if (feeder_mode)
	{
		analogWrite(hopper_pwm_pin, feeder_speed_array[feeder_speed_selector]);
	}

}

void feeder_toggle_mode()
{
	// turns on/off the feeder. Does not modify current speed setting.

	if (feeder_mode)
	{
		feeder_mode = false;
		analogWrite(hopper_pwm_pin, 0);
		return;
	}
	else
	{
		feeder_mode = true;
		analogWrite(hopper_pwm_pin, feeder_speed_array[feeder_speed_selector]);
	}
}

void belt_toggle_mode()
{
	if (belt_mode)
	{
		belt_mode = false;
		digitalWrite(belt_control_pin, LOW);
	}
	else
	{
		belt_mode = true;
		digitalWrite(belt_control_pin, HIGH);
	}
}