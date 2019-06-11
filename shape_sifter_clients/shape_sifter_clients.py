""" The contents of this are only used for R&D """

# 3rd party imports
import time

# 1st party imports
import shape_sifter_tools.shape_sifter_tools as ss
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


def dev_mule(pipe_me_recv, pipe_me_send):
    """ Dummy client for testing and R&D """

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

