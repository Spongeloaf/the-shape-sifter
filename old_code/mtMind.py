# 3rd party im ports
from fastai.vision import *
import time

# 1st party imports
import shape_sifter_tools.shape_sifter_tools as ss
import ss_classes
from ss_classes import ServerInit, ClientParams


def main(params: ClientParams):

    logger = ss.create_logger(params.log_fname_const, params.log_level, 'mtmind')
    logger.info('mtmind running! Log level set to {}'.format(params.log_level))
    image_path = params.google_path + "mt_mind\\captured_images\\"
    logger.debug(image_path)

    logger.debug("loading learner....")
    mtmind = load_learner(params.model_path, params.model_fname)
    logger.info("Learner loaded!")

    while True:
        t_start = time.perf_counter()

        if params.pipe_recv.poll(0):
            part: ss_classes.PartInstance = params.pipe_recv.recv()
            pred: Category = mtmind.predict(part.part_image)
            part.category_name = pred[0].obj
            part.server_status = 'mtm_done'
            params.pipe_send.send(part)

        t_stop = time.perf_counter()
        t_duration = t_stop - t_start
        if t_duration < params.tick_rate:
            time.sleep(params.tick_rate - t_duration)


def stand_alone(client_params: ClientParams):
    """ Only used for performance testing """

    image_path = client_params.google_path + "mt_mind\\captured_images\\"
    print(image_path)
    logger = ss.create_logger(client_params.log_fname_const, client_params.log_level, 'mtmind')
    logger.info('mtmind running! Log level set to {}'.format(client_params.log_level))

    mtmind = load_learner(client_params.model_path, client_params.model_fname)
    image1 = open_image("C:\\Users\Development\\Google Drive\\software_dev\\the_shape_sifter\\assets\\images\\wheels\\172616422709.png")
    image2 = open_image("C:\\Users\Development\\Google Drive\\software_dev\\the_shape_sifter\\assets\\images\\wheels\\172616422709.png")
    image3 = open_image("C:\\Users\Development\\Google Drive\\software_dev\\the_shape_sifter\\assets\\images\\wheels\\172616422709.png")

    ss_classes.PartInstance()

    input("Press Enter to continue...")
    t_start = time.perf_counter()
    result = mtmind.predict(image1)
    t_stop = time.perf_counter()
    print(t_stop - t_start)
    print(result[0])

    input("Press Enter to continue...")
    t_start = time.perf_counter()
    result = mtmind.predict(image2)
    t_stop = time.perf_counter()
    print(t_stop - t_start)
    print(result)

    input("Press Enter to continue...")
    t_start = time.perf_counter()
    result = mtmind.predict(image3)
    t_stop = time.perf_counter()
    print(t_stop - t_start)
    print(result)

    input("Press Enter to continue...")
    t_start = time.perf_counter()
    result = mtmind.predict(image1)
    t_stop = time.perf_counter()
    print(t_stop - t_start)
    print(result)

    input("Press Enter to continue...")
    t_start = time.perf_counter()
    result = mtmind.predict(image2)
    t_stop = time.perf_counter()
    print(t_stop - t_start)
    print(result)

    input("Press Enter to continue...")
    t_start = time.perf_counter()
    result = mtmind.predict(image3)
    t_stop = time.perf_counter()
    print(t_stop - t_start)
    print(result)


if __name__ == '__main__':
    init = ServerInit()
    parameters = ClientParams(init, 'mtmind')
    stand_alone(parameters)
