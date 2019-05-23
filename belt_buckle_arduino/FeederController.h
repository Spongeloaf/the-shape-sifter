/*
 * FeederController.h
 *
 * Created: 4/23/2019 3:30:43 PM
 *  Author: spongeloaf
 */




#ifndef FEEDERCONTROLLER_H_
#define FEEDERCONTROLLER_H_
#include "bb_parameters.h"


class FeederController{
	// This object provides a control interface to the part feeder.
	// This class ensures that the motor operates safely.
	// The motor cannot be switched from stationary to full power, due to the immense current drawn by a stationary motor.
	// When the motor starts, it is only allowed a minimal duty cycle for the first [startup_delay] milliseconds.
	// Afterwards, the speed will be increased to the user's desired amount.
	// In the main loop, event_tick() will update the motor speed once the startup cycle is complete.
	public:
	FeederController() {};
	
	// please see function definitions for documentation.
	void speed_up();
	void speed_down();
	void toggle();
	void start();
	void stop();
	bool get_mode();
	bool get_startup();
	int get_speed();
	void start_delayed(unsigned int);
	bool get_delayed();
	

	private:
	int speed_selector = 0;																	// selects the current feeder speed from the speed_array
	bool mode = false;																		// bool to control the current speed of the belt, so we can turn it off without changing speed.
	bool startup = false;																	// true during speed limited startup phase.
	unsigned long startup_t = 0;															// tracks when the motor began to spin. Used by start() to limit current draw of stationary motor.
	unsigned long startup_delay = 2000;														// delay in milliseconds to keep the motor in the startup phase.
	const int num_speeds = 12;																// The number of speeds the feeder has. Used to unsure speed_selector doesn't go out of bounds.
	bool delayed = false;																	// Bool to control startup delay
	unsigned int delay_timer = 0;															// time in ms when the startup delay will be over.
	const int speed_array[13] = {															// holds the PWM output speeds for the feeder.
		60,
		75,
		90,
		105,
		130,
		145,
		160,
		175,
		190,
		205,
		220,
		245,
		255
	};

};


void FeederController::speed_up()
{
	// raises feeder speed unless already maxed. Does not turn on feeder.
	// TODO: Add packet notification to the server of current feed speed.

	speed_selector++;

	// true at max speed, prevents accessing speed array out of range
	if (speed_selector > num_speeds)
	{
		speed_selector = num_speeds;
	}

	// only writes to analog output if the feeder is currently running, and not currently spinning up.
	if (mode && (!(startup)))
	{
		analogWrite(gp::hopper_pwm_pin, speed_array[speed_selector]);
	}
}


void FeederController::speed_down()
{
	// raises feeder speed unless already maxed. Does not turn on feeder.
	// TODO: Add packet notification to the server of current feed speed.

	speed_selector--;

	// true at max speed, prevents accessing speed array out of range
	if (speed_selector < 0)
	{
		speed_selector = 0;
	}

	// only writes to analog output if the feeder is currently running
	if (mode && (!(startup)))
	{
		analogWrite(gp::hopper_pwm_pin, speed_array[speed_selector]);
	}

}


void FeederController::toggle()
{
	// turns on/off the feeder. Does not modify current speed setting.

	if (mode)
	{
		stop();
		return;
	}
	else
	{
		start();
	}
}


void FeederController::start()
{
	// limits startup speed of the motor. Because we need to wait for startup_delay for the motor to spin up,
	// we call this repeatedly to check the time and update the speed as required.


	// error handling. mode should never be false while startup is true.
	if (startup)
	{
		if (!mode)
		{
			mode = true;
		}
	}


	// the motor is currently in a startup phase.
	if (startup)
	{
		// check if we've past startup_delay.
		unsigned long now_t = millis();
		if ((now_t - startup_t) > startup_delay)
		{
			startup = false;
			analogWrite(gp::hopper_pwm_pin, speed_array[speed_selector]);
			Serial.println("full speed");
		}
		return;
	}
	

	if (mode)
	{
		return;		// startup must be false if we got here. abort the call; the motor is spinning as it should be.
	}
	
	// startup and mode are false. Begin startup phase.
	startup_t = millis();
	startup = true;
	mode = true;
	analogWrite(gp::hopper_pwm_pin, 20);

	Serial.println("startup");
	return;
}


void FeederController::stop()
{
	mode = false;
	startup = false;
	analogWrite(gp::hopper_pwm_pin, 0);
}


bool FeederController::get_mode()
{
	return mode;
}


bool FeederController::get_startup()
{
	return startup;
}


int FeederController::get_speed()
{
	return speed_selector;
}


void FeederController::start_delayed(unsigned int delay)
{
	// sets a delay in ms before the feeder spins up.	
	if (delayed == false)
	{
		unsigned int now = millis();
		delay_timer = now + delay;
		delayed = true;
		return;
	}
	
	if (millis() > delay_timer)
	{
		delayed = false;
		start();
	}
	
}


bool FeederController::get_delayed()
{
	return delayed;
}


#endif /* FEEDERCONTROLLER_H_ */