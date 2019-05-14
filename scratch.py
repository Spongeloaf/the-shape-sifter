from ss_server_lib import ServerInit, ClientParams, check_taxi, check_cf, send_cf
import multiprocessing
import time
import random


def start_clients(server_init: ServerInit):
    """ starts the clients

    :return = List of client processes """

    # from taxidermist.taxidermist import main as taxi
    from taxidermist.taxidermist import taxi_sim as taxi
    from shape_sifter_clients.shape_sifter_clients import classifist

    # list of client processes
    clients = []

    # start taxidermist
    taxi_params = ClientParams(server_init, "taxi")
    taxi = multiprocessing.Process(target=taxi, args=(taxi_params,))
    clients.append(taxi)
    taxi.start()
    server_init.logger.info('taxidermist started')

    # start classifist
    classifist_params = ClientParams(server_init, "classifist")
    classifist_proc = multiprocessing.Process(target=classifist, args=(classifist_params,))
    clients.append(classifist_proc)
    classifist_proc.start()
    server_init.logger.info('classifist started')

    return clients


def main():
    server = ServerInit()
    start_clients(server)
    time.sleep(5)

    while True:
        check_taxi(server)
        check_cf(server)

        for part in server.part_list:
            if part.server_status == 'new':
                i = random.randint(0,1)
                if i == 0:
                    part.category_name = 'brick'
                else:
                    part.category_name = 'plate'

                send_cf(server, part)

            if part.server_status == 'cf_done':
                print(vars(part))
                server.part_list.remove(part)

        time.sleep(1)


if __name__ == '__main__':
    main()

