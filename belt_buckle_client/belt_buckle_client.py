# 1st party imports
import shape_sifter_tools.shape_sifter_tools as ss
from ss_server_lib import ClientParams, ServerInit

# 3rd party imports
import serial
import time
import random
from datetime import datetime


class BbClient:
    """This is the software interface for the conveyor belt controller.
        We differentiate the hardware belt buckle from this piece of software
        by calling the hardware the 'belt buckle', and this software 'belt buckle client'

        This client acts as a proxy only. It converts serial strings to part objects and vice versa.
        All logic relating to system operation is handled by the BB or server."""

    # TODO: Change BB_init so that it simply waits for '[BB_ONLINE]' and follows a startup routine. This will handle BB reboots the same way as initial boot.
    # TODO: Add version number checking to BB_init
    # TODO: Add bin config downloading to BB_init
    # TODO: re-work the client to have a slower loop, but more intelligent use of CPU time. Right now it loops too quickly


    def __init__(self, params: ClientParams):
        self.params = params
        self.logger = ss.create_logger(params.log_fname_const, params.log_level, 'belt_buckle_client')
        self.bb_status = False
        self.ser = serial.Serial(params.com_port, params.baud_rate, writeTimeout=0, timeout=0.001, inter_byte_timeout=0.0007)

        # give the Belt Buckle time to start
        time.sleep(1)

        if self.params.skip_handshake == "False":
            self.start_bb()


    def start_bb(self):
        self.logger.info('Belt Buckle is up on {0} with log level {1}. Waiting for BB handshake'.format(self.ser.name, params.log_level))
        if __name__ == '__main__':
            self.ser.write(b'Waiting for BB handshake')

        while True:
            t_start = time.perf_counter()
            boot_read = self.ser.readline()
            # boot_read = boot_read.decode("ascii")

            if boot_read == b'[BB_ONLINE]':
                break

            t_stop = time.perf_counter()
            t_duration = t_stop - t_start
            if t_duration < 0.017:
                time.sleep(0.017 - t_duration)

        self.logger.info("BB Online using {}".format(self.params.com_port))


    def check_server(self):
        # check server #
        if self.params.pipe_recv.poll(0):
            server_command_received: ss.BbPacket = self.params.pipe_recv.recv()
            try:
                if server_command_received.command_type == 'BBC':  # the part has been assigned a to a bin. Send the B command.
                    if server_command_received.status_code == '200':

                        self.logger.debug('server > bb: {}'.format(server_command_received.byte_string))

                        self.ser.write(server_command_received.byte_string)
                        self.logger.critical(server_command_received.byte_string)
                    else:
                        self.logger.error('received bad BbPacket from server:{}').format(vars(server_command_received))

            except AttributeError:
                self.logger.critical("Attribute Error while executing server_command_received")
                self.logger.critical(vars(server_command_received))


    def check_serial(self):
        # read the serial buffer
        buffer = ''
        if self.ser.in_waiting >= 29:
            while self.ser.in_waiting > 0:
                read = self.ser.read()
                char = read.decode("utf-8")
                if char == '[':
                    buffer = char
                elif char == ']':
                    buffer += char
                    self.logger.debug(buffer)
                    self.dispatch_packet( buffer)
                    break
                else:
                    buffer += char


    def dispatch_packet(self, string: str):
        self.logger.debug("bb > server {}".format(string))
        self.logger.critical(string)
        bb_command_receive = ss.BbPacket(serial_string=string)
        if bb_command_receive.status_code == '200':
            self.params.pipe_send.send(bb_command_receive)
        else:
            self.logger.error('malformed packet received from belt buckle: {}'.format(vars(bb_command_receive)))


    def test_run(self):
        self.logger.info("Belt buckle is running in test mode. No hardware interaction!")
        while True:
            time.sleep(self.params.tick_rate)
            if self.params.pipe_recv.poll(0):
                server_command_received: ss.BbPacket = params.pipe_recv.recv()
                server_command_received = None


    def main_client(self):
        """main loop"""
        while True:
            t_start = time.perf_counter()
            self.check_server()
            time.sleep(0.01)        # wait for a response
            self.check_serial()
            t_stop = time.perf_counter()
            t_duration = t_stop - t_start

            if t_duration < params.tick_rate:
                time.sleep(params.tick_rate - t_duration)


    def main_standalone(self):
        """main loop"""
        self.ser.write(b'Server sim online')
        while True:
            t_start = time.perf_counter()
            self.server_sim()
            time.sleep(0.01)        # wait for a response
            self.check_serial()
            t_stop = time.perf_counter()
            t_duration = t_stop - t_start

            if t_duration < params.tick_rate:
                time.sleep(params.tick_rate - t_duration)


    def server_sim(self):
        r = random.randint(0, 60)
        if r == 1:
            now = datetime.now()
            instance_id = now.strftime("%H%M%S%f")
            packet_a = ss.BbPacket(command='A', argument='0000', payload=instance_id, command_type='BBC')
            packet_b = ss.BbPacket(command='B', argument='0007', payload=instance_id, command_type='BBC')
            self.ser.write(packet_a.byte_string)
            time.sleep(0.01)
            self.ser.write(packet_b.byte_string)


def main(params: ClientParams):
    bb = BbClient(params)
    bb.main_client()


if __name__ == '__main__':
    init = ServerInit()
    params = ClientParams(init, 'bb')
    bb = BbClient(params)
    bb.main_standalone()

