import shape_sifter_tools
import multiprocessing
import logging
import pandas
import psutil
import os
import time


# we need this for subprocessing. Not sure why.
if __name__ == '__main__':

    p = psutil.Process(os.getpid())
    # set to normal priority, this is windows only, on Unix use ps.nice(19)
    p.nice(psutil.NORMAL_PRIORITY_CLASS)

    #initialize empty items such as prev_id and job list
    prev_id = ''
    jobs = []
    text = pandas.DataFrame([[1, 2], [3, 4]], index=['A', 'B'], columns=['X', 'Y'])

    # #start taxidermist
    # pipe_from_taxi, pipe_to_taxi = multiprocessing.Pipe(duplex=True)
    # p1 = multiprocessing.Process(target=shape_sifter_tools.taxidermist, args=(pipe_to_taxi,))
    # jobs.append(p1)
    # taxi = p1.start()
    # print('taxidermist started')

    #Start mtmind simulator
    pipe_from_mtm, pipe_to_mtm = multiprocessing.Pipe(duplex=True)
    p2 = multiprocessing.Process(target=shape_sifter_tools.part_instance_sim, args=(pipe_to_mtm,))
    jobs.append(p2)
    mtm = p2.start()
    print('shapesifter started')

    # start classifist
    pipe_from_classifist, pipe_to_classifist = multiprocessing.Pipe(duplex=True)
    p3 = multiprocessing.Process(target=shape_sifter_tools.classifist, args=(pipe_from_classifist, pipe_to_classifist))
    jobs.append(p3)
    clasifist = p3.start()
    print('classifist started')

    #main loop
    while True:

        t_start = time.perf_counter()

        # #checks if the taxi pipe has something yet, if so, read that shit
        # if pipe_from_taxi.poll(0) == True:

        #checks if the mtm pipe has something yet, if so, read that shit and do stuff
        if pipe_from_mtm.poll(0) == True:

            # read from the pipe and store the contents for use
            read_part = pipe_from_mtm.recv()
            print(read_part.instance_id)

            # check to see if the current part instance id has changed
            if read_part.instance_id != prev_id:
                # print('new part!')
                pipe_to_classifist.send(read_part.part_number)
                prev_id = read_part.instance_id

        # #checks if the classifist pipe has something yet, if so, read that shit
        if pipe_from_classifist.poll(0) == True:
            print("received from CF")
            text = pipe_from_classifist.recv()
            print(text)
            # send to BB

        # #checks if the belt buckle pipe has something yet, if so, read that shit
        # if pipe_from_BB.poll(0) == True:

        t_stop= time.perf_counter()
        t_duration = t_stop - t_start
        if t_duration < 0.017:
            time.sleep(0.017 - t_duration)



    # pipe_to_mtm.close()
    # p.join()
