# 3rd party imports
import time
import sqlite3

# 1st party imports
import ss_classes
from shape_sifter_tools import shape_sifter_tools as ss
from ss_classes import ClientParams


def classifist(client_params: ClientParams):
    """ Assigns parts to bins """

    # TODO: Eliminate SQL and replace this with a config file.

    logger = ss.create_logger(client_params.log_fname_const, client_params.log_level, 'classifist')
    logger.info('classifist running! Log level set to {}'.format(client_params.log_level))
    while True:
        t_start = time.perf_counter()

        if client_params.pipe_recv.poll(0):

            read_part: ss_classes.PartInstance = client_params.pipe_recv.recv()
            sqconn = sqlite3.connect(client_params.server_db_fname_const)
            sqcur = sqconn.cursor()


            # evaluate query
            for part_bin in sqcur.execute("SELECT * FROM table_bin_config"):
                if part_bin[1] == 'part':
                    if part_bin[2] == str(read_part.part_number):  # assume all values are strings, just to be safe!
                        read_part.bin_assignment = part_bin[0]
                        read_part.server_status = 'cf_done'
                        client_params.pipe_send.send(read_part)
                        break

                if part_bin[1] == 'category_name':
                    if part_bin[2] == str(read_part.category_name):  # assume all values are strings, just to be safe!
                        read_part.bin_assignment = part_bin[0]
                        read_part.server_status = 'cf_done'
                        client_params.pipe_send.send(read_part)
                        break
            else:
                read_part.bin_assignment = 0
                read_part.server_status = 'cf_done'
                client_params.pipe_send.send(read_part)

            sqconn.close()

        t_stop = time.perf_counter()
        t_duration = t_stop - t_start
        if t_duration < 0.017:
            time.sleep(0.017 - t_duration)