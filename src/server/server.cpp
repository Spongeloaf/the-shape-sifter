// This is the Shape Sifter server.
#include <chrono>
#include <thread>
#include <iostream>
#include "../common/ss_classes.h"
#include "server.h"
#include <INIReader/INIReader.h>
#include <spdlog/spdlog.h>

Server::Server()
{
	LoadConfig();
}

bool Server::LoadConfig()
{
	INIReader reader(m_configPath);
	if (reader.ParseError() != 0)
	{
		assert(!"Error in config file! Aborting.");
		return false;
	}
	return true;
	spdlog::set_level(spdlog::level::debug);
	spdlog::info("Welcome to spdlog!");
}

int main()
{
	Server server = Server();
	//	# 3rd party imports
	//import time
	//
	//# 1st party imports. Safe to use from x import *
	//import ss_classes
	//import ss_server_lib as slib
	//
	//
	//# needed for multiprocessing
	//if __name__ == '__main__':
	//
	//    init = ss_classes.ServerInit()
	//    clients, bb = init.start_clients()
	//    mode = ss_classes.ServerMode()
	//    server = slib.Server(init, bb)
	//
	 // main loop
	while (true)
	{
		// loop timer
		auto start = std::chrono::high_resolution_clock::now();
		//if mode.check_taxi:
		//    server.check_taxi()
		//
		//if mode.check_mtm:
		//    server.check_mtm()
		//
		//if mode.check_cf:
		//    server.check_cf()
		//
		//if mode.check_bb:
		//    server.check_bb()
		//
		//if mode.iterate_active_part_db:
		//    server.iterate_part_list()
		//
		//server.check_suip(mode)
		//server.send_part_list_to_suip()
		//
		// global_tick_rate is the time in milliseconds of each loop, taken from settings.ini
		auto end = std::chrono::high_resolution_clock::now();
		std::chrono::duration<double, std::milli> elapsed = end - start;
		std::cout << "elapsed: " << elapsed.count() << "\r\n";
		if (elapsed < kUpdateInterval)
		{
			std::this_thread::sleep_for(kUpdateInterval - elapsed);
		}
	}
}