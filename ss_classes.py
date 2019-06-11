import configparser
import multiprocessing
from genericpath import isfile

from fastai.vision import open_image, Image
from shape_sifter_tools import shape_sifter_tools as ss


""" Common classes for all clients """


class ServerInit:
    """Write something here"""

    def __init__(self):

        # get google drive directory
        self.google_path = self.get_google_drive_path()

        # declarations and initializations. All objects ending with _const are NOT to be modified at run time!
        self.server_config_file_const = self.google_path + '\\settings.ini'
        self.server_log_file_const = self.google_path + '\\log\\log_server.txt'
        self.server_sort_log_file_const = self.google_path + '\\log\\sort_log.txt'
        self.server_db_fname_const = self.google_path + '\\db\\shape_sifter.sqlite'
        self.server_db_template_const = self.google_path + '\\db\\shape_sifter_template.sqlite'
        self.part_log_fname_const = self.google_path + '\\log\\part_log.txt'
        self.active_part_table_const = ('active_part_db',)   # the fuck is this for? I think it's the name of the DB?
        self.dummy_image = open_image(self.google_path + '\\dummy.png')
        self.prev_id = ''
        self.bb_message_len = 29
        self.pipes = Pipes()


        # create logger, default debug level. Level will be changed once config file is loaded
        self.logger = ss.create_logger(self.server_log_file_const, 'DEBUG')

        # TODO: Move this somewhere else! Make a function out of it along with the next block below
        # if config file doesn't exist, create one. Defaults are in shape_sifter_tools.py
        if not isfile(self.server_config_file_const):
            self.logger.info("config file doesn't exist. Creating...")
            self.create_server_config()

        # load config file and assign values.
        # TODO: Turn this into a function that verifies the settings and returns an object.
        # TODO: It should also handle key exceptions. It should also log it's actions. I should also do some of these TODOs someday.
        self.server_config = self.load_server_config()

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
        self.suip_list_len = int(self.server_config['suip']['list_len'])

        self.bb_com_port = self.server_config['bb']['com_port']
        self.bb_baud_rate = int(self.server_config['bb']['baud_rate'])
        self.bb_skip_handshake = self.server_config['bb']['skip_handshake']
        self.bb_log_level = self.server_config['bb']['log_level']
        self.bb_timeout = self.server_config['bb']['timeout']
        self.bb_test_run = bool(int(self.server_config['bb']['test_run']))


        # replace logger with level set by config file
        self.logger = ss.create_logger(self.server_log_file_const, self.server_log_level, 'server')
        self.part_log = ss.create_logger(self.part_log_fname_const, 'DEBUG', 'part_log')
        


    @staticmethod
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


    def start_clients(self):
        """ starts the clients

        :return = List of client processes """

        from taxidermist.taxidermist import main as taxi
        # from taxidermist.taxidermist import taxi_sim as taxi
        # from shape_sifter_clients.shape_sifter_clients import mt_mind_sim
        from mt_mind.mtMind import main as mtmind
        from classifist.classifist import classifist
        from suip.suip import main as gui
        from belt_buckle_client.belt_buckle_client import BbClient

        # list of client processes
        clients = []

        # start bb
        bb_params = ClientParams(self, 'bb')
        bb = BbClient(bb_params)

        # start taxidermist
        taxi_params = ClientParams(self, "taxi")
        taxi_proc = multiprocessing.Process(target=taxi, args=(taxi_params,), name='taxi')
        clients.append(taxi_proc)
        taxi_proc.start()
        self.logger.info('taxidermist started with pid: {0}'.format(taxi_proc.pid))

        # Start mtmind
        mtmind_params = ClientParams(self, "mtmind")
        mtmind_proc = multiprocessing.Process(target=mtmind, args=(mtmind_params,), name='mtmind')
        clients.append(mtmind_proc)
        mtmind_proc.start()
        self.logger.info('mtmind started with pid: {0}'.format(mtmind_proc.pid))

        # start classifist
        classifist_params = ClientParams(self, "classifist")
        classifist_proc = multiprocessing.Process(target=classifist, args=(classifist_params,), name='classifist')
        clients.append(classifist_proc)
        classifist_proc.start()
        self.logger.info('classifist started with pid: {0}'.format(classifist_proc.pid))

        # start the SUIP
        suip_params = ClientParams(self, "suip")
        suip_proc = multiprocessing.Process(target=gui, args=(suip_params,), name='suip')
        clients.append(suip_proc)
        suip_proc.start()
        self.logger.info('suip started with pid: {0}'.format(suip_proc.pid))

        return clients, bb


    def create_server_config(self):
        """creates a new, default, server config file.
        Right now it does nothing useful, but we may need it later!
        See trello documentation for log file naming conventions.
        The server name was little more than a novelty to begin with.
        But I like the idea of critical errors being written in the second person.
        'Steve has encountered an error'
        """

        config = configparser.ConfigParser()

        # default values:
        config['server'] = {'server_log_level': 'debug',
                            'server_name': 'Steve',
                            'bb_com_port': 'COM3',
                            'bb_baud_rate': '19200'
                            }
        config_file = open(self.server_config_file_const, 'x')
        config.write(config_file)  # the new ini file is created in the root directory


    def load_server_config(self):
        """loads a config file and applies it to the server. """

        # try to load the config file. If this fails, the server exits.
        try:
            config = configparser.ConfigParser()
            config.read(self.server_config_file_const)
            return config
        except KeyError:
            self.logger.critical('Config file KeyError. Check config file for missing values!')
            exit("Config file KeyError. Check config file for missing values!")


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
            self.pipe_recv = server_init.pipes.taxi_recv_server
            self.pipe_send = server_init.pipes.taxi_send_server
            self.belt_mask = server_init.taxi_belt_mask
            self.video_source = server_init.taxi_video_source
            self.view_video = server_init.taxi_view_video

        if client_type == "mtmind":
            self.log_fname_const = self.google_path + "\\log\\log_mtmind.txt"
            self.model_path = "{}{}".format(server_init.google_path, server_init.mtm_model_path)
            self.model_fname = server_init.mtm_model_fname
            self.log_level = server_init.mtm_log_level
            self.pipe_recv = server_init.pipes.mtm_recv_server
            self.pipe_send = server_init.pipes.mtm_send_server

        if client_type == "classifist":
            self.log_fname_const = self.google_path + "\\log\\log_classifist.txt"
            self.log_level = server_init.cf_log_level
            self.pipe_recv = server_init.pipes.classifist_recv
            self.pipe_send = server_init.pipes.classifist_send

        if client_type == "bb":
            self.log_fname_const = self.google_path + "\\log\\log_bb.txt"
            self.log_level = server_init.bb_log_level
            self.pipe_recv = server_init.pipes.bb_recv
            self.pipe_send = server_init.pipes.bb_send
            self.com_port = server_init.bb_com_port
            self.baud_rate = server_init.bb_baud_rate
            self.timeout = server_init.bb_timeout
            self.skip_handshake = server_init.bb_skip_handshake
            self.test_run = server_init.bb_test_run
            self.bb_message_len = server_init.bb_message_len

        if client_type == "suip":
            self.log_fname_const = self.google_path + "\\log\\log_suip.txt"
            self.log_level = server_init.suip_log_level
            self.pipe_recv = server_init.pipes.suip_recv
            self.pipe_send = server_init.pipes.suip_send
            self.pipe_part_list = server_init.pipes.part_list_recv
            self.list_len = server_init.suip_list_len


class Pipes:
    def __init__(self):
        # taxi pipes
        self.taxi_recv_server, self.server_send_taxi = multiprocessing.Pipe(duplex=False)
        self.server_recv_taxi, self.taxi_send_server = multiprocessing.Pipe(duplex=False)

        # mt mind pipes
        self.mtm_recv_server, self.server_send_mtm = multiprocessing.Pipe(duplex=False)
        self.server_recv_mtm, self.mtm_send_server = multiprocessing.Pipe(duplex=False)

        # classifist pipes
        self.classifist_recv, self.server_send_cf = multiprocessing.Pipe(duplex=False)
        self.server_recv_cf, self.classifist_send = multiprocessing.Pipe(duplex=False)

        # belt buckle pipes
        self.bb_recv, self.server_send_bb = multiprocessing.Pipe(duplex=False)
        self.server_recv_bb, self.bb_send = multiprocessing.Pipe(duplex=False)

        # suip pipes
        self.suip_recv, self.server_send_suip = multiprocessing.Pipe(duplex=False)
        self.server_recv_suip, self.suip_send = multiprocessing.Pipe(duplex=False)
        self.part_list_recv, self.part_list_send = multiprocessing.Pipe(duplex=False)


class ServerMode:
    """Server video_source object. Stores attributes used to control the state of the server."""

    def __init__(self):
        self.iterate_active_part_db = False
        self.check_taxi = False
        self.check_mtm = False
        self.check_cf = False
        self.check_bb = False


class PartInstance:
    """A single part from the belt."""

    def __init__(self,
                 part_image: Image = None,
                 instance_id: str = '',
                 capture_time: float = 0.0,
                 part_number: str ='',
                 category_number: str ='',
                 part_color: str ='',
                 category_name: str ='',
                 bin_assignment: int =0,
                 camera_offset: int = -1,
                 server_status: str ='',
                 bb_status: str ='',
                 serial_string: str= '',
                 t_taxi: float = 0.0,
                 t_mtm: float = 0.0,
                 t_cf: float = 0.0,
                 t_added: float = 0.0,
                 t_assigned: float = 0.0):

        self.instance_id = instance_id
        self.capture_time = capture_time
        self.part_number = part_number
        self.category_number = category_number
        self.part_image = part_image
        self.part_color = part_color
        self.category_name = category_name
        self.bin_assignment = bin_assignment
        self.camera_offset = camera_offset
        self.server_status = server_status
        self.bb_status = bb_status
        self.serial_string = serial_string
        self.t_taxi = t_taxi
        self.t_mtm = t_mtm
        self.t_cf = t_cf
        self.t_added = t_added
        self.t_assigned = t_assigned


class SuipLadle:
    """An object class for sending and receiving commands from the SUIP"""
    def __init__(self, command: str = '', info: str = '', payload=None):
        self.command = command
        self.info = info
        self. payload = payload


class BbPacket:
    """A class containing all of the necessary parts of a belt buckle packet.
    All attributes are strings, CSUM is a string of bytes

    <XAAAA123456789012CSUM>

    """

    def __init__(self, command: str = '',
                 argument: str = '0000',
                 payload: str = '',
                 csum: str = '',
                 type: str = '',
                 status: str = ''):

        self.command = command              # command string
        self.payload = payload              # payload string
        self.csum = csum                    # calculated CSUM in bytes
        self.type = type
        self.status = status

        if isinstance(argument, float):
            argument = int(argument)

        if isinstance(argument, int):
            argument = str(argument)

        self.argument = argument.zfill(4)

    def __str__(self):
        return '{}-{}-{}-{}-{}'.format(self.command, self.argument, self.payload, self.type, self.status)