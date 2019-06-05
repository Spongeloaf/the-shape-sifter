# 3rd party imports
import time
from cv2 import Stitcher
import sys
import sqlite3

# 1st party imports
import shape_sifter_tools.shape_sifter_tools as ss
import ss_classes
import suip.suip as gui
from ss_classes import ClientParams


def mt_mind_sim(client_params: ClientParams):
    """Simulates behavior of the MTMind by adding a random part number and category to a part instance"""

    logger = ss.create_logger(client_params.log_fname_const, client_params.log_level, 'mt_mind')
    logger.info('part sim running!')
    import random

    while True:
        t_start = time.perf_counter()
        if client_params.pipe_recv.poll(0):

            part = client_params.pipe_recv.recv()
            part.part_number = random.randint(3001, 3002)

            category = random.randint(1, 4)
            if category == 1:
                part_category = 5  # brick
                category_name = 'brick'
            elif category == 2:
                part_category = 26  # plate
                category_name = 'plate'

            elif category == 3:
                part_category = 21  # cone
                category_name = 'cone'

            elif category == 4:
                part_category = 37  # tile
                category_name = 'tile'

            else:
                part_category = -1
                category_name = 'null'

            part.category_name = category_name
            part.part_color = str(random.randint(1, 20))
            part.server_status = 'mtm_done'
            client_params.pipe_send.send(part)
            # print("mtm sim just ident'd part {0}".format(part.instance_id))

        t_stop = time.perf_counter()
        t_duration = t_stop - t_start
        if t_duration < 0.017:
            time.sleep(0.017 - t_duration)


def classifist(client_params: ClientParams):
    """Classi-FIST me baby!"""

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
            for bin in sqcur.execute("SELECT * FROM table_bin_config"):
                if bin[1] == 'part':
                    if bin[2] == str(read_part.part_number):  # assume all values are strings, just to be safe!
                        read_part.bin_assignment = bin[0]
                        read_part.server_status = 'cf_done'
                        client_params.pipe_send.send(read_part)  # return results to server
                        break

                if bin[1] == 'category_name':
                    if bin[2] == str(read_part.category_name):  # assume all values are strings, just to be safe!
                        read_part.bin_assignment = bin[0]
                        read_part.server_status = 'cf_done'
                        client_params.pipe_send.send(read_part)  # return results to server
                        break
            else:
                read_part.bin_assignment = 0
                read_part.server_status = 'cf_done'
                client_params.pipe_send.send(read_part)  # return results to server

            sqconn.close()

        t_stop = time.perf_counter()
        t_duration = t_stop - t_start
        if t_duration < 0.017:
            time.sleep(0.017 - t_duration)


def dev_mule(pipe_me_recv, pipe_me_send):
    """Simulates behavior of the MTMind by adding a random part number and category to a part instance"""

    logger = ss.create_logger('log\\log_part_instance_sim.txt', 'INFO', 'dev_mule')
    logger.info('part sim running!')
    time.sleep(20)
    while True:
        t_start = time.perf_counter()
        if pipe_me_recv.poll(0) == True:
            part = pipe_me_recv.recv()
            print(part.instance_id)
            print(part.part_number)
            print('------------------------------------')

        t_stop = time.perf_counter()
        t_duration = t_stop - t_start
        if t_duration < 0.017:
            time.sleep(0.017 - t_duration)


