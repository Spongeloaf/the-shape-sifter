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
// A humble class to print arrays for deugging purposes.

public:
	
	ArrayPrint() {};
	
	void array(char*);
	void array(unsigned long*);
	// void array_2d();			Broke as fuck
	//void part_index_full();
	//void part_index_single();

};


void ArrayPrint::array(char* to_be_printed){                    // prints an array of characters
	for (int i = 0; i <= gp::print_size; i++)
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
	for (int i = 0; i <= gp::print_size; i++)
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


#endif /* ARRAYPRINT_H_ */