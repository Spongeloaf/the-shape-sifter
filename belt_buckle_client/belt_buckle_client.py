# 1st party imports
import shape_sifter_tools.shape_sifter_tools as ss
from ss_server_lib import ClientParams

# 3rd party imports
import serial
import time


def main(params: ClientParams):
    """This is the software interface for the conveyor belt controller.
    We differentiate the hardware belt buckle from this piece of software
    by calling the hardware the 'belt buckle', and this software 'belt buckle client'

    This client acts as a proxy only. It converts serial strings to part objects and vice versa.
    All logic relating to system operation is handled by the BB or server."""

    # TODO: Change BB_init so that it simply waits for '[BB_ONLINE]' and follows a startup routine. This will handle BB reboots the same way as initial boot.
    # TODO: Add version number checking to BB_init
    # TODO: Add bin config downloading to BB_init
    # TODO: re-work the client to have a slower loop, but more intelligent use of CPU time. Right now it loops too quickly

    # BB init
    bb_status = False
    serial_read_str = ''
    logger = ss.create_logger(params.log_fname_const, params.log_level, 'belt_buckle_client')

    # run without a com port. Dumps the pipe to nowhere. For development purposes only!
    if params.test_run:
        logger.info("Belt buckle is running in test mode. No hardware interaction!")
        while True:
            time.sleep(params.tick_rate)
            if params.pipe_recv.poll(0):
                server_command_received: ss.BbPacket = params.pipe_recv.recv()
                server_command_received = None

    # start serial port
    ser = serial.Serial(params.com_port,
                        params.baud_rate,
                        writeTimeout=0,
                        timeout=0.001,
                        inter_byte_timeout=0.0007)

    # Allow Arduino to boot
    time.sleep(1)

    # when skip_handshake is true we skip waiting for the BB to report that it's online.
    if params.skip_handshake != 'True':
        logger.info('Belt Buckle is up on {0} with log level {1}. Waiting for BB handshake'.format(ser.name, params.log_level))
        while not bb_status:
            t_start = time.perf_counter()

            boot_read = ser.readline()
            # boot_read = boot_read.decode("ascii")

            if boot_read == b'[BB_ONLINE]':
                bb_status = True

            t_stop = time.perf_counter()
            t_duration = t_stop - t_start
            if t_duration < 0.017:
                time.sleep(0.017 - t_duration)

    logger.info("bitch we runnin'")

    # main loop
    while True:

        t_start = time.perf_counter()

        # TODO: Make the TRY/Except sections below into a function and call it once per pipe.

        # TODO: remove this block so the server handles all BB packets. We are not having the taxi send things directly

        # check taxi #
        # depreciated!
        # if params.pipe_recv.poll(0):
        #     taxi_command_received: ss.BbPacket = params.pipe_recv.recv()
        #     try:
        #         if taxi_command_received.type == 'BBC':  # the part is fresh from the taxidermist, send the 'A' command.
        #             if taxi_command_received.status_code == '200':
        #
        #                 print('taxi > bb: {}'.format(taxi_command_received.byte_string))
        #
        #                 ser.write(taxi_command_received.byte_string)
        #             else:
        #                 logger.error('received bad BbPacket from server:{}').format(vars(taxi_command_received))
        #
        #     except AttributeError:
        #         logger.critical("Attribute Error while executing taxi_command_received")
        #         logger.critical(vars(taxi_command_received))

        # check server #
        if params.pipe_recv.poll(0):
            server_command_received: ss.BbPacket = params.pipe_recv.recv()
            try:
                if server_command_received.type == 'BBC':  # the part has been assigned a to a bin. Send the B command.
                    if server_command_received.status_code == '200':

                        logger.info('server > bb: {}'.format(server_command_received.byte_string))

                        ser.write(server_command_received.byte_string)
                    else:
                        logger.error('received bad BbPacket from server:{}').format(vars(server_command_received))

            except AttributeError:
                logger.critical("Attribute Error while executing server_command_received")
                logger.critical(vars(server_command_received))

        # Read the serial port. We drop any extra characters before the packet initiator by splitting the string, and keeping only the last item.
        serial_read_byt = ser.read()

        serial_read_char = serial_read_byt.decode("utf-8")

        if serial_read_char == '[':
            serial_read_str = '['

        elif serial_read_char == ']':
            serial_read_str = serial_read_str + serial_read_char
            logger.info("bb > server {}".format(serial_read_str))
            bb_command_receive = ss.BbPacket(serial_string=serial_read_str)
            if bb_command_receive.status_code == '200':
                params.pipe_send.send(bb_command_receive)
            else:
                logger.debug('malformed packet received from belt buckle: {}'.format(vars(bb_command_receive)))
            serial_read_str = ''

        elif serial_read_char != '':
            serial_read_str = serial_read_str + serial_read_char

        t_stop = time.perf_counter()
        t_duration = t_stop - t_start
        if t_duration < params.tick_rate:
            time.sleep(params.tick_rate - t_duration)
