""" This is the Shape Sifter. Run this file to run the machine. """

# 3rd party imports
import time

# 1st party imports. Safe to use from x import *
import ss_classes
import ss_server_lib as slib


# needed for multiprocessing
if __name__ == '__main__':

    init = ss_classes.ServerInit()
    clients, bb = init.start_clients()
    mode = ss_classes.ServerMode()
    server = slib.Server(init, bb)

    # main loop
    while True:

        # main loop timer.
        t_start = time.perf_counter()

        if mode.check_taxi:
            server.check_taxi()

        if mode.check_mtm:
            server.check_mtm()

        if mode.check_cf:
            server.check_cf()

        if mode.check_bb:
            server.check_bb()

        if mode.iterate_active_part_db:
            server.iterate_part_list()

        server.check_suip(mode)
        server.send_part_list_to_suip()

        # global_tick_rate is the time in milliseconds of each loop, taken from settings.ini
        t_stop = time.perf_counter()
        t_duration = t_stop - t_start
        if t_duration < init.global_tick_rate:
            time.sleep(init.global_tick_rate - t_duration)
