/*
 * BinController.h
 *
 * Created: 4/26/2019 1:12:89 PM
 *  Author: spongeloaf
 */



#include "bb_parameters.h"



#ifndef BINCONTROLLER_H_
#define BINCONTROLLER_H_



class BinController{

/*

A word about bin numbers: Bin 0 is a valid number. 
Parts may be assigned to this bin to ensure they go off the end of the belt without triggering a any alarms.
Therefore, some of the private functions which for-loop over the various bindexes start with i=1, instead of i=0.

TODO: trigger an alarm when a part runs off the belt and wasn't assigned to do so.

*/

public:
	
	BinController() 
	{
		set_bin_defaults(); 
		init_pins();
	}

	void on_airjet(int);
	void off_airjets();
	void test_outputs(int);
	unsigned long get_din_dist(int bin);
	void set_bin_dist(int bin, unsigned long dist);
	void set_bin_defaults();
	void init_pins();
	int check_past_bin(int bin, unsigned long dist);



private:
	
	unsigned long bin_width;
	
	// this magic number is limited by hardware. It's not likely to ever change.
	int number_of_bins = 16;
	
	// stores the time that the airjet was turned on; used to turn them off after ::bin_airjet_time
	unsigned long airjet_timers[number_of_bins + 1];
	
	// time in milliseconds that the air jet stays on
	const unsigned long bin_airjet_time;													 
		
	// stores distance ints for each bin location
	unsigned long bin_distances[number_of_bins + 1];							 
	
	// the bin output pin numbers. These are also unlikely to ever change.
	const int bin_pindex[number_of_bins + 1] = {                                    
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
		37 };
	
	unsigned long current_distance;
	unsigned long travelled_distance;
	unsigned long previous_distance;
};


void BinController::on_airjet(int bin)
{
	// stash the time that the airjet was turned on, we'll turn it off later in the airjet
	airjet_timers[bin] = millis();																															
	digitalWrite(bin_pindex[bin], HIGH);
}


void BinController::off_airjets()
{
	for (int i = 0; i < number_of_bins; i++ )
	{
		if (millis() > (airjet_timers[i] + bin_airjet_time))
		{
			digitalWrite(bin_pindex[i], LOW);
			airjet_timers[i] = 0;
		}
	}
}


void BinController::test_outputs(int t)
{
	Serial.println("Testing outputs...");
	for (int i = 1; i <= number_of_bins; i++ )							// setting up our bin outputs and writing values to HIGH.
	{
		digitalWrite(bin_pindex[i], HIGH);
		delay(t);
		digitalWrite(bin_pindex[i], LOW);
		delay(t);
		Serial.print("output: ");
		Serial.println(bin_pindex[i]);
	}
	Serial.println("Test complete");
}


unsigned long BinController::get_din_dist(int bin)
{
	return bin_distances[bin];
}


void BinController::set_bin_dist(int bin, unsigned long dist)
{
	bin_distances[bin] = dist;
}


void BinController::set_bin_defaults()
{
	bin_airjet_time = 200;
	
	bin_width = 4158;
	
	bin_distances[0] = 0;
	bin_distances[1] = 6445;
	bin_distances[2] = 6445;
	bin_distances[3] = 10603;
	bin_distances[4] = 10603;
	bin_distances[5] = 14761;
	bin_distances[6] = 14761;
	bin_distances[7] = 18919;
	bin_distances[8] = 18919;
	
	// off the end of the belt, if we're still using the original one.	
	bin_distances[9] = 23077;
	bin_distances[10] = 23077;
	bin_distances[11] = 23077;
	bin_distances[12] = 23077;
	bin_distances[13] = 23077;
	bin_distances[14] = 23077;
	bin_distances[15] = 23077;
	bin_distances[16] = 23077;
}


void BinController::init_pins()
{
	// setting up our bin outputs and writing values to LOW.
	for (int i = 1; i <= number_of_bins; i++ )																	
	{
		pinMode(bin_pindex[i], OUTPUT);
		digitalWrite(bin_pindex[i], LOW);
	}
}


int BinController::check_past_bin(int bin, unsigned long part_dist)
{
	// returns an int indicating where a part is relative to a bin.
	
	// past the bin
	if (part_dist > bin_distances[bin] + bin_width) return -1;
	
	// in front of the bin, ready for airjet
	if (part_dist > bin_distances[bin]) return 1;
	
	// not in front of bin yet.
	return 0;
}



#endif /* BINCONTROLLER_H_ */