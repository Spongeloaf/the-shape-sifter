
# 3rd party im ports
from fastai.vision import *
import time

# 1st party imports
import shape_sifter_tools.shape_sifter_tools as ss
from ss_server_lib import ClientParams, ServerInit


def main(client_params: ClientParams):
    image_path = client_params.google_path + "mt_mind\\captured_images\\"
    print(image_path)
    logger = ss.create_logger(client_params.log_fname_const, client_params.log_level, 'mtmind')
    logger.info('mtmind running! Log level set to {}'.format(client_params.log_level))

    mtmind = load_learner(client_params.model_path, client_params.model_fname)

    while True:
        t_start = time.perf_counter()

        if client_params.pipe_recv.poll(0):
            read_part: ss.part_instance = client_params.pipe_recv.recv()
            print(mtmind.predict(read_part.part_image))

        t_stop = time.perf_counter()
        t_duration = t_stop - t_start
        if t_duration < 0.017:
            time.sleep(0.017 - t_duration)


def stand_alone(client_params: ClientParams):
    image_path = client_params.google_path + "mt_mind\\captured_images\\"
    print(image_path)
    logger = ss.create_logger(client_params.log_fname_const, client_params.log_level, 'mtmind')
    logger.info('mtmind running! Log level set to {}'.format(client_params.log_level))

    mtmind = load_learner(client_params.model_path, client_params.model_fname)
    image1 = open_image("C:\\google_drive\\software_dev\\the_shape_sifter\\mt_mind\\lego_v4\\valid\wheel\\183508738698.png")
    image2 = open_image("C:\\google_drive\\software_dev\\the_shape_sifter\\mt_mind\\lego_v4\\valid\\tile\\165128210491.png")
    image3 = open_image("C:\\google_drive\\software_dev\\the_shape_sifter\\mt_mind\\lego_v4\\valid\\tile\\164749628490.png")


    ss.part_instance()

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
    params = ClientParams(init, 'mtmind')

    stand_alone(params)
