"""A word about my SQL statements.
I know they violate good coding practice. using .format on my SQL statements is not very secure.
The solutions however, are bazookas to my projects housefly. I do not think that fixing them will benefit this project,
as I intend it to stay within my own home and off the internet for now.
Besides, all the critical DBs are made on the fly from templates, so ruining them is no real problem.
So I am making the following TO DO conditional upon the software being released to the public:"""
# TODO: Learn the correct methods for sanitizing SQL commands.


# ------- Pre-alpha to do's: ------- #
# TODO: Build a framework for handling ACKs from the belt buckle
# TODO: Add a part log
# TODO: Make sure as few lines of code as possible are between taxidermist and belt buckle
# TODO: make the part instance attributes into enumerators. -> Why? I don't remember wanting this!

# ------- Post-Alpha to do's: ------- #
# TODO: Build client watchdogs. Get PIDs when a client starts and try to spin up a new one if it hangs/crashes
# TODO: figure out how to handle too many parts on the belt.
# TODO: should the config DBs be .inis?
# TODO: add sort config functionality, the SUIP should be able to have the server create/save/load new config dbs.
# TODO: add handlers for clients, so they can be halted in the event of critical failure, without killing everything.


# Third party imports
import time

# first party imports. Safe to use from x import *
import ss_server_lib as slib    # slib contains all of our server loop and control functions

# we need this for sub-processing. Not sure why.
if __name__ == '__main__':

    server = slib.server_init()
    mode = slib.server_mode()

    # main loop
    while True:

        # our main loop timer. Keeps the server ticking at 60hz. See t_stop at the end of the loop.
        t_start = time.perf_counter()
        slib.check_suip(server, mode)

        if mode.check_taxi:
            slib.check_taxi(server)
            # taxi.taxidermist_sim(server)

        if mode.iterate_active_part_db:
            slib.iterate_active_part_db(server)

        if mode.check_mtm:
            slib.check_mtm(server)

        if mode.check_cf:
            slib.check_cf(server)

        if mode.check_bb:
            slib.check_bb(server)

        # keeps the server ticking at 60hz. Measures the duration from the start of the loop (t_start) and waits until 17ms have passed.
        t_stop = time.perf_counter()
        t_duration = t_stop - t_start
        if t_duration < 0.017:
            time.sleep(0.017 - t_duration)
