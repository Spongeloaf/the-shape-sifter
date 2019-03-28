# A newer and better version exists in shape_sifter_clients.py
# -------------------------------------------OBSOLETE----------------------------------------------------
# -------------------------------------------OBSOLETE----------------------------------------------------
# -------------------------------------------OBSOLETE----------------------------------------------------
# -------------------------------------------OBSOLETE----------------------------------------------------
# -------------------------------------------OBSOLETE----------------------------------------------------
# -------------------------------------------OBSOLETE----------------------------------------------------
# A newer and better version exists in shape_sifter_clients.py

import serial
import time
import shape_sifter_tools as ss
import random

com_port = 'COM4'
baud_rate = 57600

# -------------------------------------------OBSOLETE----------------------------------------------------
# -------------------------------------------OBSOLETE----------------------------------------------------
# A newer and better version exists in shape_sifter_clients.py
# -------------------------------------------OBSOLETE----------------------------------------------------
# -------------------------------------------OBSOLETE----------------------------------------------------




"""an intense internal debate was had over whether or not we should use a buffer for commands.
Eventually it was decided that we do not need something so complex, at least not at this stage.
So for now, we simply stop accepting server commands until the desired ACk is received."""

# BB init
bb_status = False
logger = ss.create_logger('log\\log_belt_buckle.txt', 'INFO')
ser = serial.Serial(com_port, baud_rate, writeTimeout=0.005, timeout=0.005, inter_byte_timeout = 0.0005)
time.sleep(1)
logger.info('Belt Buckle is up on {0}'.format(ser.name))

# while bb_status == False:
#     t_start = time.perf_counter()
#
#     boot_read = ser.readline()
#     boot_read = boot_read.decode("utf-8")
#
#     if boot_read == '[BB_ONLINE]':
#         bb_status = True
#         print("bitch we runnin'")
#
#     t_stop = time.perf_counter()
#     t_duration = t_stop - t_start
#     if t_duration < 0.017:
#         time.sleep(0.017 - t_duration)

# main loop
while True:
    t_start = time.perf_counter()

    # if last command has been ACKed, check pipe from server
    # execute server command

    bb_read_byt = ser.read_until(b']')          # The terminator of BB to Server strings is ']'
    bb_read_str = bb_read_byt.decode("utf-8")   # received serial string is bytes encoded so we convert to UTF8.

    if bb_read_str == '':
        continue

    bb_read_obj = ss.parse_bb_packet_incoming(bb_read_str)

    if bb_read_obj.status_code != '200':
        logger.error('{0} {1}'.format(bb_read_obj.status_code, bb_read_obj.status_string))
        continue

    if bb_read_obj.type == 'TEL':
        # have server parse command
        pass

    if bb_read_obj.type == 'ACK':
        # check ACK against last command sent.
        pass

    t_stop = time.perf_counter()
    t_duration = t_stop - t_start
    if t_duration < 0.017:
        time.sleep(0.017 - t_duration)

# [TEL-X-9999-XXXXXXXXXXXX-CSUM]    [ACK-X-999-XXXXXXXXXXXX-CSUM]
