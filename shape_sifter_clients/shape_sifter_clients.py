import random
import time
from cv2 import Stitcher
import shape_sifter_tools as ss
import shape_sifter_gui_v2 as gui
import sys
import sqlite3


def mt_mind_sim(pipe_me_recv, pipe_me_send, log_level):
    """Simulates behavior of the MTMind by adding a random part number and category to a part instance"""

    logger = ss.create_logger('log\\log_part_instance_sim.txt',log_level, 'mt_mind')
    logger.info('part sim running!')

    while True:
        t_start = time.perf_counter()
        if pipe_me_recv.poll(0) == True:

            part = pipe_me_recv.recv()
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
            pipe_me_send.send(part)
            # print("mtm sim just ident'd part {0}".format(part.instance_id))

        t_stop = time.perf_counter()
        t_duration = t_stop - t_start
        if t_duration < 0.017:
            time.sleep(0.017 - t_duration)


def classifist(pipe_me_recv, pipe_me_send, db_fname_const, log_level):
    """Classi-FIST me baby!"""

    # working_part_obj is read from the MM and compared to the last part, and dropped if it is different
    # We will need to change this to accomodate timestamps in the future.
    # If we dont use timestamps, consecutive parts of the same number will be dropped.
    # print("part number:{0}\n".format(working_part_obj))

    logger = ss.create_logger('log\\log_classifist.txt', log_level, 'classifist')
    logger.info('classifist running! Log level set to {}'.format(log_level))
    while True:
        t_start = time.perf_counter()

        if pipe_me_recv.poll(0) == True:

            read_part: ss.part_instance = pipe_me_recv.recv()

            # time to write a whole new loop using THE POWER OF SQLITE
            # open connection to SQL
            sqconn = sqlite3.connect(db_fname_const)
            sqcur = sqconn.cursor()

            # TODO: Fix this to call fetchone() instead of calling an iterator on cursor.execute!    <------ why tho?
            # TODO: Really though, looping fethcall isn't possible until we upgrade the venv
            # evaluate query
            for bin in sqcur.execute("SELECT * FROM table_bin_config"):
                if bin[1] == 'part':
                    if bin[2] == str(read_part.part_number):  # assume all values are strings, just to be safe!
                        read_part.bin_assignment = bin[0]
                        read_part.server_status = 'cf_done'
                        pipe_me_send.send(read_part)  # return results to server
                        break

                if bin[1] == 'cat':
                    if bin[2] == str(read_part.category_number):  # assume all values are strings, just to be safe!
                        read_part.bin_assignment = bin[0]
                        read_part.server_status = 'cf_done'
                        pipe_me_send.send(read_part)  # return results to server
                        break
            else:
                read_part.bin_assignment = 0
                read_part.server_status = 'cf_done'
                pipe_me_send.send(read_part)  # return results to server

            sqconn.close()                # close SQL

            # print('-------------\n\rFrom CF:\n\rpart {0}\n\rcategory {3} {2}\n\rassigned to bin {1}\n\r-------------'
            # .format(read_part.part_number,read_part.bin_assignment,read_part.category_name, read_part.category_number))

        t_stop = time.perf_counter()
        t_duration = t_stop - t_start
        if t_duration < 0.017:
            time.sleep(0.017 - t_duration)


def stitcher(image_list, self=None):
    # TODO: the fuck is this? can it be removed?
    pass
    Stitcher.stitch(self, image_list)


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


def suip(pipe_me_recv, pipe_me_send, active_part_db_fname_const):
    """ The sorting machine UI
        All fucntion defs are in shape_sifter_gui.py
        The GUI consists of a pyQT gui connected to the active part DB and the part log DB,
        with a pipe to the server for command/control signaling. This signaling is handled by
        a class of objects called ladles. The ladle definition is shape_sifter_tools.py
    """

    suip_app = gui.QApplication(sys.argv)
    gui.set_dark_theme(suip_app)
    suip_window = gui.suip_window_class(active_part_db_fname_const, pipe_me_recv, pipe_me_send,)
    suip_window.show()
    suip_window.raise_()
    suip_app.exec_()
