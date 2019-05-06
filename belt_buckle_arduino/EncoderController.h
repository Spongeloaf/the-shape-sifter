/*
 * EncoderCOntroller.h
 *
 * Created: 4/23/2019 3:30:43 PM
 *  Author: spongeloaf
 */



#ifndef ENCODERCONTROLLER_H_
#define ENCODERCONTROLLER_H_
#include "bb_parameters.h"
#include <Wire.h>


class EncoderController{
public:
	
	EncoderController() 
	{
		Wire.begin();
		status = true;
	};
	
	unsigned long get_dist();
	bool is_running();
	void start_sim();
	void stop_sim();
	bool get_sim();
	void toggle_sim();
	
private:
	
	bool status;
	bool old_status;
	unsigned long old_dist = 0;
	
	// simulates a moving belt; for testing without having the hardware hooked up.
	unsigned long enc_sim();
	bool sim_mode = false;	
};


// get the distance from the encoder. Credit: https:// thewanderingengineer.com/2015/05/06/sending-16-bit-and-32-bit-numbers-with-arduino-i2c/
unsigned long EncoderController::get_dist()																											

{
	// This method has not been protected from rollovers at all.
	// That protection should be handled by whomever calls get_dist.
	
	if (sim_mode) 
	{
		return enc_sim();
	}
	
	unsigned long distance;
	byte a,b,c,d;

	Wire.requestFrom(wire_address, 4);																						
	if (Wire.available() > 0)
	{
		a = Wire.read();
		b = Wire.read();
		c = Wire.read();
		d = Wire.read();

		// bit shifting our four individual bytes into one unsigned long int
		distance = a;
		distance = (distance << 8) | b;
		distance = (distance << 8) | c;
		distance = (distance << 8) | d;

		return distance;
	}
	return 1;
}


bool EncoderController::is_running()
{
	unsigned long new_dist = get_dist();
	
	if (old_dist == new_dist) return false;
	
	old_dist = new_dist;
	
	return true;
}


unsigned long EncoderController::enc_sim()
{
	// This method has not been protected from rollovers at all.
	// That protection should be handled by whomever calls get_dist.
	return sim_scaler * millis();
}


void EncoderController::toggle_sim()
{
	(sim_mode) ? stop_sim() : start_sim();
}


void EncoderController::start_sim()
{
	sim_mode = true;
}


void EncoderController::stop_sim()
{
	sim_mode = false;
}


bool EncoderController::get_sim()
{
	return sim_mode;
}


#endif /* ENCODERCONTROLLER_H_ */