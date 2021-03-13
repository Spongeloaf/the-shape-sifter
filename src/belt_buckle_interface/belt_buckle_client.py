# 1st party imports
from ss_classes import *

# 3rd party imports
import serial
import time


class BbClient:
    """
    This is the software interface for the conveyor belt controller.
    We differentiate the hardware belt buckle from this piece of software
    by calling the hardware the 'belt buckle', and this software 'belt buckle client'

    This client acts as a proxy only. It converts serial strings to part objects and vice versa.
    All logic relating to system operation is handled by the BB or server.
    """

    # TODO: Add version number checking to BB_init
    # TODO: Add bin config downloading to BB_init

    def __init__(self, params: ClientParams):
        self.params = params
        self.logger = ss.create_logger(params.log_fname_const, params.log_level, 'belt_buckle_client')
        self.comlog = ss.create_logger(params.google_path + '\\log\\log_com.txt', params.log_level, 'belt_buckle_comlog')
        self.bb_status = False
        self.serial_timeout = 0.01
        self.ser = serial.Serial(params.com_port, params.baud_rate, writeTimeout=0, timeout=0.004, inter_byte_timeout=0.0007)

        # give the Belt Buckle time to start
        time.sleep(1)

        if self.params.skip_handshake == "False":
            self.wait_bb_handshake()
        else:
            self.ser.write(b"BB client up. No handshake.\n\r")


    def wait_bb_handshake(self):
        self.logger.info('Belt Buckle is up on {0}. Waiting for BB handshake'.format(self.ser.name))
        if __name__ == '__main__':
            self.ser.write(b'Waiting for BB handshake')

        while True:
            t_start = time.perf_counter()

            boot_read = self.ser.readline()
            if boot_read == b'[BB_ONLINE]':
                break

            t_stop = time.perf_counter()
            t_duration = t_stop - t_start
            if t_duration < 0.017:
                time.sleep(0.017 - t_duration)

        self.logger.info("BB Online using {}".format(self.params.com_port))


    def check_serial(self):
        """ Checks the serial port for any commands received """
        if self.ser.in_waiting < self.params.bb_message_len:
            return ''

        serial_read_str = ''
        self.comlog.critical('start check serial')
        t_start = time.perf_counter()

        while True:
            serial_read_byt = self.ser.read()
            serial_read_char = serial_read_byt.decode("utf-8")
            self.comlog.debug(serial_read_char)

            if serial_read_char == '[':
                serial_read_str = '['
                self.comlog.debug('new packet')
                t_start = time.perf_counter()

            elif serial_read_char == ']':
                serial_read_str = serial_read_str + serial_read_char
                self.logger.info("bb > server {}".format(serial_read_str))
                return serial_read_str

            elif serial_read_char != '':
                serial_read_str = serial_read_str + serial_read_char

            t_loop = time.perf_counter()

            if (t_loop - t_start) > self.serial_timeout:
                self.comlog.debug('time out')
                return ''


    def parse_serial_string(self, serial_string):

        packet = BbPacket()

        if len(serial_string) != 29:
            packet.status = 'bad'
            self.logger.debug('Bad packet length in parse_serial_string(): {}'.format(serial_string))

        # true for incoming commands from the BB
        if serial_string.startswith('[') and serial_string.endswith(']'):
            try:
                serial_split = serial_string.strip('[')
                serial_split = serial_split.strip(']')

                # parse command
                serial_split = serial_split.split('-')

                # serial_string = serial_string
                packet.type = serial_split[0]
                packet.command = serial_split[1]
                packet.response = serial_split[2]
                packet.payload = serial_split[3]

                if packet.type == 'ACK' or packet.type == 'TEL':
                    packet.status = 'ok'

            except IndexError or AttributeError:
                self.logger.debug('Bad serial_string in parse_serial_string(): {}'.format(serial_string))
                packet.status = 'Index or Attribute error'

        return packet


    def dispatch_packet(self, packet: BbPacket):
        serial_string = '<{}{}{}CSUM>\n'.format(packet.command, packet.argument, packet.payload)
        self.logger.info('server > bb {}'.format(serial_string))
        self.ser.write(bytes(serial_string, "UTF-8"))


    def send_command_a(self, argument, payload):
        packet = BbPacket(command='A', argument=argument, payload=payload)
        self.dispatch_packet(packet)


    def send_command_b(self, argument, payload):
        packet = BbPacket(command='B', argument=argument, payload=payload)
        self.dispatch_packet(packet)


    def send_command_o(self, payload):
        packet = BbPacket(command='O', argument='xxxx', payload=payload)
        self.dispatch_packet(packet)


    def send_command_m(self, argument):
        packet = BbPacket(command='M', argument=argument, payload='xxxxxxxxxxxx')
        self.dispatch_packet(packet)

