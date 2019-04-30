/*
 * ArrayPrint.h
 *
 * Created: 4/23/2019 12:23:44 PM
 *  Author: spongeloaf
 */ 




#ifndef ARRAYPRINT_H_
#define ARRAYPRINT_H_
#include "bb_parameters.h"



class ArrayPrint{
public:
	
	ArrayPrint() {};
	
	void array(char*);
	void array(unsigned long*);
	// void array_2d();			Broke as fuck
	//void part_index_full();
	//void part_index_single();

};


void ArrayPrint::array(char* to_be_printed){                    // prints an array of characters
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


void ArrayPrint::array(unsigned long* to_be_printed){                    // prints an array of characters
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

/*
void ArrayPrint::array_2d() {
	
	for ( int i = 0; i < index_length; ++i ) {               //  loop through array's rows
		
		for ( int j = 0; j < payload_length; ++j )
		{                //  loop through columns of current row
			Serial.print (index_payload[ i ][ j ] );
		}
		Serial.print ("\n") ; //  start new line of output
	}
}
*/

/*
void ArrayPrint::part_index_full() {
	
	Serial.println("  Payload    :  Dist. : Bin") ;
	for ( int i = 0; i < index_length; ++i )                     //  loop through array's rows
	{
		
		for ( int j = 0; j < payload_length; ++j )
		{                //  loop through columns of current row
			Serial.print (index_payload[ i ][ j ] );
		}
		
		Serial.print(" : ") ;
		Serial.print(part_index_distance[i]);
		Serial.print(" : ") ;
		Serial.print(part_index_bin[i]);
		Serial.print("\n") ; //  start new line of output
	}
}
*/

/*
void ArrayPrint::part_index_single(int i) {
	
	Serial.println("  Payload    :  Dist. : Bin") ;
	
	for ( int j = 0; j < payload_length; ++j )
	{                //  loop through columns of current row
		Serial.print (index_payload[ i ][ j ] );
	}
	
	Serial.print(" : ") ;
	Serial.print(part_index_distance[i]);
	Serial.print(" : ") ;
	Serial.print(part_index_bin[i]);
	Serial.print("\n") ; //  start new line of output
}
*/


#endif /* ARRAYPRINT_H_ */