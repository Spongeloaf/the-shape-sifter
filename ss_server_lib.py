# Third party imports
import multiprocessing
import time
from os.path import isfile
from fastai.vision import open_image, Image

# first party imports. Safe to use from x import *
import shape_sifter_tools.shape_sifter_tools as ss


""" This file contains all of the shape sifter server specific functions.
Common functions and classes used by more than the server are stored elsewhere."""

# TODO: Properly plan belt buckle timeouts and status changes


class ServerInit:
    """Write something here"""

    def __init__(self):

        # get google drive directory
        self.google_path = get_google_drive_path()

        # declarations and initializations. All objects ending with _const are NOT to be modified at run time!
        self.server_settings_file_const = self.google_path + '\\settings.ini'
        self.server_log_file_const = self.google_path + '\\log\\log_server.txt'
        self.server_sort_log_file_const = self.google_path + '\\log\\sort_log.txt'
        self.server_db_fname_const = self.google_path + '\\db\\shape_sifter.sqlite'
        self.server_db_template_const = self.google_path + '\\db\\shape_sifter_template.sqlite'
        self.part_log_fname_const = self.google_path + '\\log\\part_log.txt'
        self.active_part_table_const = ('active_part_db',)   # the fuck is this for? I think it's the name of the DB?
        self.dummy_image = open_image(self.google_path + '\\dummy.png')
        self.prev_id = ''
        self.part_list = []

        # create logger, default debug level. Level will be changed once config file is loaded
        self.logger = ss.create_logger(self.server_log_file_const, 'DEBUG')

        # create sorting log
        self.sort_log = ss.create_logger(self.server_sort_log_file_const, 'INFO')

        # TODO: Move this somewhere else! Make a function out of it along with the next block below
        # if config file doesn't exist, create one. Defaults are in shape_sifter_tools.py
        if not isfile(self.server_settings_file_const):
            self.logger.info("config file doesn't exist. Creating...")
            ss.create_server_config(self.server_settings_file_const)

        # load config file and assign values.
        # TODO: Turn this into a function that verifies the settings and returns an object.
        # TODO: It should also handle key exceptions. It should also log it's actions. I should also do some of these TODOs someday.
        self.server_config = ss.load_server_config(self.server_settings_file_const, self.logger)

        self.global_tick_rate = float(self.server_config['server']['global_tick_rate'])

        self.server_log_level = self.server_config['server']['log_level']
        self.server_bb_ack_timeout = self.server_config['server']['bb_ack_timeout']

        self.taxi_log_level = self.server_config['taxi']['log_level']
        self.taxi_belt_mask = self.google_path + "\\assets\\taxidermist\\" + self.server_config['taxi']['belt_mask']
        self.taxi_video_source = self.server_config['taxi']['video_source']
        self.taxi_view_video = self.server_config['taxi']['view_video']

        self.mtm_log_level = self.server_config['mtm']['log_level']
        self.mtm_model_path = self.server_config['mtm']['model_path']
        self.mtm_model_fname = self.server_config['mtm']['model_fname']

        self.cf_log_level = self.server_config['cf']['log_level']

        self.suip_log_level = self.server_config['suip']['log_level']

        self.bb_com_port = self.server_config['bb']['com_port']
        self.bb_baud_rate = self.server_config['bb']['baud_rate']
        self.bb_skip_handshake = self.server_config['bb']['skip_handshake']
        self.bb_log_level = self.server_config['bb']['log_level']
        self.bb_timeout = self.server_config['bb']['timeout']
        self.bb_test_run = bool(int(self.server_config['bb']['test_run']))

        # replace logger with level set by config file
        self.logger = ss.create_logger(self.server_log_file_const, self.server_log_level, 'server')
        self.part_log = ss.create_logger(self.part_log_fname_const, 'DEBUG', 'part_log')

        # pipe from taxidermist to BB
        # TODO: Remove this pipe. The taxidermist should not communicate directly with the belt buckle.
        self.pipe_bb_recv_taxi, self.pipe_taxi_send_bb = multiprocessing.Pipe(duplex=False)
        
        # taxi pipes
        self.pipe_taxi_recv_server, self.pipe_server_send_taxi = multiprocessing.Pipe(duplex=False)
        self.pipe_server_recv_taxi, self.pipe_taxi_send_server = multiprocessing.Pipe(duplex=False)

        # mt mind pipes
        self.pipe_mtm_recv_server, self.pipe_server_send_mtm = multiprocessing.Pipe(duplex=False)
        self.pipe_server_recv_mtm, self.pipe_mtm_send_server = multiprocessing.Pipe(duplex=False)
        
        # classifist pipes
        self.pipe_classifist_recv, self.pipe_server_send_cf = multiprocessing.Pipe(duplex=False)
        self.pipe_server_recv_cf, self.pipe_classifist_send = multiprocessing.Pipe(duplex=False)
        
        # belt buckle pipes
        self.pipe_bb_recv, self.pipe_server_send_bb = multiprocessing.Pipe(duplex=False)
        self.pipe_server_recv_bb, self.pipe_bb_send = multiprocessing.Pipe(duplex=False)

        # suip pipes
        self.pipe_suip_recv, self.pipe_server_send_suip = multiprocessing.Pipe(duplex=False)
        self.pipe_server_recv_suip, self.pipe_suip_send = multiprocessing.Pipe(duplex=False)
        self.pipe_part_list_recv, self.pipe_part_list_send = multiprocessing.Pipe(duplex=False)
        

class ClientParams:
    """ For clients to get server config parameters. """

    def __init__(self, server_init: ServerInit, client_type: str):
        self.google_path = server_init.google_path
        self.server_db_fname_const = server_init.server_db_fname_const
        self.log_level = server_init.server_log_level                   # uses server log level if unspecified
        self.tick_rate = server_init.global_tick_rate

        if client_type == "taxi":
            self.log_fname_const = self.google_path + "\\log\\log_taxi.txt"
            self.log_level = server_init.taxi_log_level
            self.pipe_recv = server_init.pipe_taxi_recv_server
            self.pipe_send = server_init.pipe_taxi_send_server
            self.belt_mask = server_init.taxi_belt_mask
            self.video_source = server_init.taxi_video_source
            self.view_video = server_init.taxi_view_video

        if client_type == "mtmind":
            self.log_fname_const = self.google_path + "\\log\\log_mtmind.txt"
            self.model_path = "{}{}".format(server_init.google_path, server_init.mtm_model_path)
            self.model_fname = server_init.mtm_model_fname
            self.log_level = server_init.mtm_log_level
            self.pipe_recv = server_init.pipe_mtm_recv_server
            self.pipe_send = server_init.pipe_mtm_send_server

        if client_type == "classifist":
            self.log_fname_const = self.google_path + "\\log\\log_classifist.txt"
            self.log_level = server_init.cf_log_level
            self.pipe_recv = server_init.pipe_classifist_recv
            self.pipe_send = server_init.pipe_classifist_send

        if client_type == "bb":
            self.log_fname_const = self.google_path + "\\log\\log_bb.txt"
            self.log_level = server_init.bb_log_level
            self.pipe_recv = server_init.pipe_bb_recv
            self.pipe_send = server_init.pipe_bb_send
            self.com_port = server_init.bb_com_port
            self.baud_rate = server_init.bb_baud_rate
            self.timeout = server_init.bb_timeout
            self.skip_handshake = server_init.bb_skip_handshake
            self.tick_rate = 0.0005
            self.test_run = server_init.bb_test_run

        if client_type == "suip":
            self.log_fname_const = self.google_path + "\\log\\log_suip.txt"
            self.log_level = server_init.suip_log_level
            self.pipe_recv = server_init.pipe_suip_recv
            self.pipe_send = server_init.pipe_suip_send
            self.pipe_part_list = server_init.pipe_part_list_recv


class ServerMode:
    """Server video_source object. Stores attributes used to control the state of the server."""

    def __init__(self):
        self.iterate_active_part_db = False
        self.check_taxi = False
        self.check_mtm = False
        self.check_cf = False
        self.check_bb = False


def iterate_part_list(server: ServerInit):
    """
    Iterate active part db. Once per main server loop we check for actionable statuses on all current parts.
    Actions are taken where necessary. Each If statement below represents and actionable status.
    see the documentation on Trello for a complete list of what all the statuses mean.

    :param server: server init object
    :return: none
    """

    for part in server.part_list:

        # checks for any parts that have not been acknowledged by the belt buckle
        if part.bb_status == 'wait_ack':
            check_bb_timeout(server, part)
            continue

        # checks for any parts that were sorted by the belt buckle
        if part.bb_status == 'sorted':
            server.sort_log.info('id:{}, bin{}, cat: {}, pnum: {}'.format(part.instance_id, part.bin_assignment, part.category_name, part.part_number))
            server.part_list.remove(part)
            continue

        # checks for parts that have been lost by the belt buckle. A part is lost if it misses it's bin and goes off the end of the belt.
        if part.bb_status == 'lost':
            server.sort_log.info('id:{}, bin{}, cat: {}, pnum: {}, NOT SORTED!'.format(part.instance_id, part.bin_assignment, part.category_name, part.part_number))
            server.part_list.remove(part)
            continue

        # server status = new; the part was just received from the taxidermist. Send it to the MTM
        if part.server_status == 'new':
            send_bb_a(server, part)
            send_mtm(server, part)
            continue

        # server status = mtm_done; the part was returned frm the MTMind, send it to the classifist.
        if part.server_status == 'mtm_done':
            send_cf(server, part)
            continue

        # server_status = cf_done; the part was returned from the classifist. Send the bin assignment to the belt buckle.
        if part.server_status == 'cf_done':
            send_bb_b(server, part)
            continue


def check_suip(server, mode):
    """Check for commands sent by the SUIP"""
    if server.pipe_server_recv_suip.poll(0):
        suip_command = server.pipe_server_recv_suip.recv()
        try:
            # starts the server main loop
            if suip_command.command == 'server_control_run':
                mode.iterate_active_part_db = True
                mode.check_taxi = True
                mode.check_mtm = True
                mode.check_cf = True
                mode.check_bb = True

            # stops the server main loop
            if suip_command.command == 'server_control_halt':
                mode.iterate_active_part_db = False
                mode.check_taxi = False
                mode.check_mtm = False
                mode.check_cf = False
                mode.check_bb = False

        except AttributeError:
            server.logger.error("Attribute Error in check_suip(). See dump on next line")
            server.logger.error("{0}".format(suip_command))


def check_taxi(server: ServerInit):
    """Checks the taxidermist for parts"""
    # checks if the taxidermist has anything for us. Sends the part to the MTM and the BB
    if server.pipe_server_recv_taxi.poll(0):
        read_part: ss.PartInstance = server.pipe_server_recv_taxi.recv()
        server.part_list.append(read_part)


def check_mtm(server: ServerInit):
    """Checks the MT mind for parts"""
    if server.pipe_server_recv_mtm.poll(0):
        read_part: ss.PartInstance = server.pipe_server_recv_mtm.recv()

        for part in server.part_list:
            if part.instance_id == read_part.instance_id:
                server.part_list.remove(part)
                server.part_list.append(read_part)


def check_cf(server: ServerInit):
    """Checks the classifist for parts"""
    if server.pipe_server_recv_cf.poll(0):
        read_part: ss.PartInstance = server.pipe_server_recv_cf.recv()

        for part in server.part_list:
            if part.instance_id == read_part.instance_id:
                server.part_list.remove(part)
                server.part_list.append(read_part)


def check_bb(server: ServerInit):
    """Checks the belt buckle for messages"""
    # TODO: Add support for all the response codes below. Remove all the PASS commands and replace them with proper commands
    if server.pipe_server_recv_bb.poll(0):
        bb_read_part: ss.BbPacket = server.pipe_server_recv_bb.recv()
        if bb_read_part.status_code == '200':

            # TEL commands notify the server that...
            if bb_read_part.type == 'TEL':

                # ...a part has been sorted. Remove it from the part_list.
                if bb_read_part.command == 'C':
                    for part in server.part_list:
                        if bb_read_part.payload == part.instance_id:
                            part.bb_status = 'sorted'

                # ...a part has gone off the end of the belt
                if bb_read_part.command == 'F':
                    for part in server.part_list:
                        if bb_read_part.payload == part.instance_id:
                            part.bb_status = 'lost'

                # ...a handshake has been received
                if bb_read_part.command == 'H':
                    pass

                # ...the belt buckle has requested to download the bin config
                if bb_read_part.command == 'D':
                    server.logger.debug('Received download command from belt buckle')
                    pass

            # ACK commands inform the server that a previous BBC command sent to the BB was received, understood, and executed. Any errors will be indicated by the response code
            if bb_read_part.type == 'ACK':

                # the previous BBC command was executed correctly. Update the active_part_DB
                if bb_read_part.response == '200':
                    # ...a part has been sorted
                    if bb_read_part.command == 'B':
                        for part in server.part_list:
                            if bb_read_part.payload == part.instance_id:
                                part.bb_status = 'sorted'

                else:
                    server.logger.error("slib.check_bb failed. response code = {}. Packet:{}".format(bb_read_part.response, vars(bb_read_part)))

        else:
            server.logger.error("A packet received from by the check_BB function has a bad status code. {}".format(vars(bb_read_part)))


def start_clients(server_init: ServerInit):
    """ starts the clients

    :return = List of client processes """

    from taxidermist.taxidermist import main_client as taxi
    # from shape_sifter_clients.shape_sifter_clients import mt_mind_sim
    from mt_mind.mtMind import main as mtmind
    from shape_sifter_clients.shape_sifter_clients import classifist
    from belt_buckle_client.belt_buckle_client import main as bb
    from suip.suip import main as gui

    # list of client processes
    clients = []

    # start taxidermist
    taxi_params = ClientParams(server_init, "taxi")
    taxi = multiprocessing.Process(target=taxi, args=(taxi_params,))
    clients.append(taxi)
    taxi.start()
    server_init.logger.info('taxidermist started')

    # # Start mtmind simulator
    # mtmind_params = ClientParams(server_init, "mtmind")
    # mtmind = multiprocessing.Process(target=mt_mind_sim, args=(mtmind_params,))
    # clients.append(mtmind)
    # mtmind.start()
    # server_init.logger.info('mtmind started')

    # Start mtmind
    mtmind_params = ClientParams(server_init, "mtmind")
    mtmind_proc = multiprocessing.Process(target=mtmind, args=(mtmind_params,))
    clients.append(mtmind_proc)
    mtmind_proc.start()
    server_init.logger.info('mtmind started')

    # start classifist
    classifist_params = ClientParams(server_init, "classifist")
    classifist_proc = multiprocessing.Process(target=classifist, args=(classifist_params,))
    clients.append(classifist_proc)
    classifist_proc.start()
    server_init.logger.info('classifist started')

    # start belt buckle
    belt_buckle_params = ClientParams(server_init, "bb")
    belt_buckle_proc = multiprocessing.Process(target=bb, args=(belt_buckle_params,))
    clients.append(belt_buckle_proc)
    belt_buckle_proc.start()
    server_init.logger.info('belt_buckle started')

    # start the SUIP
    suip_params = ClientParams(server_init, "suip")
    suip_proc = multiprocessing.Process(target=gui, args=(suip_params,))
    clients.append(suip_proc)
    suip_proc.start()
    server_init.logger.info('suip started')

    return clients


def send_mtm(server: ServerInit, part: ss.PartInstance):
    """Sends a part to the MTMind"""
    server.pipe_server_send_mtm.send(part)
    part.server_status = 'wait_mtm'


def send_bb_a(server: ServerInit, part: ss.PartInstance):
    """Sends the A command to the belt buckle"""
    packet = ss.BbPacket(command='A', payload=part.instance_id, type='BBC')
    if packet.status_code == '200':
        part.serial_string = packet.serial_string
        part.bb_status = 'wait_ack'
        server.pipe_server_send_bb.send(packet)
        part.capture_time = time.monotonic()  # make a time stamp so we can resend the packet if we don't get a reply in time
    else:
        server.logger.critiical("A bb packet failed in send_bb_a(). with status code: {}".format(packet.status_code))


def send_bb_b(server: ServerInit, part: ss.PartInstance):
    """Sends the B command to the belt buckle"""
    packet = ss.BbPacket(command='B', argument=part.bin_assignment, payload=part.instance_id, type='BBC')
    if packet.status_code == '200':
        part.serial_string = packet.serial_string
        part.bb_status = 'wait_ack'
        part.server_status = 'wait_sort'
        server.pipe_server_send_bb.send(packet)
        part.capture_time = time.monotonic()  # make a time stamp so we can resend the packet if we don't get a reply in time
    else:
        server.logger.critiical("A bb packet failed in send_bb_b(). with status code: {}".format(packet.status_code))


def send_cf(server: ServerInit, part: ss.PartInstance):
    part.server_status = 'wait_cf'
    server.pipe_server_send_cf.send(part)


def check_bb_timeout(server: ServerInit, part: ss.PartInstance):
    if (time.monotonic() - part.capture_time) > part.bb_timeout:
        packet = ss.BbPacket(serial_string=part.serial_string)
        if packet.status_code == '200':
            server.pipe_server_send_bb.send(packet)
            part.bb_timeout = part.bb_timeout * 2
        else:
            server.logger.error('Bad BbPacket in check_bb_timeout". Packet:{}'.format(vars(packet)))


def send_part_list_to_suip(server: ServerInit):
    """Sends the part list to the suip"""
    server.pipe_part_list_send.send(server.part_list)


def get_google_drive_path():
    """
    Get Google Drive path on windows machines.
    :return: str
    """
    # this code written by /u/Vassilis Papanikolaou from this post:
    # https://stackoverflow.com/a/53430229/10236951

    import sqlite3
    import os

    db_path = (os.getenv('LOCALAPPDATA')+'\\Google\\Drive\\user_default\\sync_config.db')
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    cursor.execute("SELECT * from data where entry_key = 'local_sync_root_path'")
    res = cursor.fetchone()
    path = res[2][4:]
    db.close()

    full_path = path + '\\software_dev\\the_shape_sifter'

    return full_path
