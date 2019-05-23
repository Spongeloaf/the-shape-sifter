# This file contains all of the function definitions for the shape sifter server.
# this should be imported using "from shape_sifter_tools import *"


import logging
import configparser
from fastai.vision import Image
from sqlite3 import Binary


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
                 server_status: str ='',
                 bb_status: str ='',
                 serial_string: str= '',
                 t_taxi: float = 0.0,
                 t_mtm: float = 0.0,
                 t_cf: float = 0.0,
                 t_assigned: float = 0.0):

        self.instance_id = instance_id
        self.capture_time = capture_time
        self.part_number = part_number
        self.category_number = category_number
        self.part_image = part_image
        self.part_color = part_color
        self.category_name = category_name
        self.bin_assignment = bin_assignment
        self.server_status = server_status
        self.bb_status = bb_status
        self.serial_string = serial_string
        self.t_taxi = t_taxi
        self.t_mtm = t_mtm
        self.t_cf = t_cf
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
                 serial_string: str = '',
                 type: str = '',
                 status_code: str = '408',
                 status_string: str = '',
                 response: str = ''):

        self.command = command              # command string
        self.argument = argument            # argument string
        self.payload = payload              # payload string
        self.csum = csum                    # calculated CSUM in bytes
        self.serial_string = serial_string  # a string of the entire command
        self.type = type                    # type of command, ACK or TEL, or BBC. TEL is a command sent by the belt buckle, ACK is an acknowledgement, BBC is a command sent to the BB.
        self.response = response          # a response code from the belt buckle - indicates if the BB processed the command correctly or not.
        self.status_code = status_code      # for internal error checking. Will be set with an error code if the parser fails for some reason.
        self.status_string = status_string  # a string to provide further error messages to

        # packets coming from the belt buckle will arrive with just a serial string. We construct the remaining bits of a packet
        if self.serial_string != '':
            try:
                # true for commands outgoing to the BB
                if serial_string.startswith('<') and serial_string.endswith('>'):
                    self.command = serial_string[1]
                    self.argument = serial_string[2:6]
                    self.payload = serial_string[6:18]
                    self.csum = serial_string[18:22]
                    self.type = 'BBC'
                    self.status_code = '200'

                    if len(serial_string) != 23:
                        self.status_code = '401'
                        self.status_string = 'Bad Packet length'

                # true for incoming commands from the BB
                elif serial_string.startswith('[') and serial_string.endswith(']'):
                    serial_split = serial_string.strip('[')
                    serial_split = serial_split.strip(']')

                    # parse command
                    serial_split = serial_split.split('-')

                    # the idea here is to create an object, and then check its parameters for correctness.
                    # TEL commands are one character longer than ACK, so we have separate rules for parsing them. Should we do something about that? I dunno.
                    # In both cases, we create the object and check the length of the string. If it's the wrong length, change the status code accordingly.
                    # More checks can be added the same way going forward. A simple IF statement followed by a status code change.

                    if serial_split[0] == 'ACK':
                        # serial_string = serial_string
                        self.type = serial_split[0]
                        self.command = serial_split[1]
                        self.response = serial_split[2]
                        self.payload = serial_split[3]
                        self.status_code = '200'
                        if len(serial_string) != 29:
                            self.status_code = '401'
                            self.status_string = 'Bad Packet length'
                        else:
                            print('wtf')

                    elif serial_split[0] == 'TEL':
                        self.type = serial_split[0]
                        self.command = serial_split[1]
                        self.argument = serial_split[2]
                        self.payload = serial_split[3]
                        self.status_code = '200'
                        if len(serial_string) != 29:
                            self.status_code = '401'
                            self.status_string = 'Bad Packet length'

                    # else is true when the packet does not start with TEL or ACK.
                    else:
                        self.status_code='406'
                        self.status_string = 'Malformed packet; Bad packet type. str:{0}'.format(serial_string)

                else:
                    self.status_code = '407'
                    self.status_string = 'malformed packet, does not have correct terminators. str: {0}'.format(serial_string)

            # Should the try statement fail, we raise an exception and then return a blank packet object with the appropriate error code
            # just like the parsing checks we can add more exception handling as needed.
            except AttributeError:
                self.status_code = '407'
                self.status_string = 'List index error while parsing. str: {0}'.format(serial_string)

        # true if we did not receive a serial string. This happens when we are given a command, argument, and payload string.
        elif self.command != '':

            if self.type == 'BBC':
                self.status_code = '200'

                # TODO: Replace this line with a robust 0 padding formatter.
                if isinstance(argument, int):
                    argument = str(argument)
                self.argument = argument.zfill(4)

                self.serial_string = '<{}{}{}CSUM>'.format(self.command, self.argument, self.payload)

            elif self.type == 'TEL':
                self.status_code = '200'
                self.serial_string = '[TEL-{}-{}-{}-CSUM]'.format(self.command, self.argument, self.payload)

            elif self.type == 'ACK':
                self.status_code = '200'
                self.serial_string = '[ACK-{}-{}-{}-CSUM]'.format(self.command, self.status_code, self.payload)

            else:
                self.status_code = '407'
                self.status_string = 'invalid or null packet type, expected BBC, ACK, or TEL, got: {}'.format(self.type)

            if self.payload == '':
                self.status_code = '409'
                self.status_string = 'Null string in attribute self.argument'

            if self.argument == '':
                self.status_code = '405'
                self.status_string = 'Null string in attribute self.argument'

        # Final step: Create a bytes version of the serial string. This happens no matter what else.
        self.byte_string = self.serial_string.encode(encoding="utf-8")


def create_server_config(settings_file_const):
    """creates a new, default, server config file.
    Right now it does nothing useful, but we may need it later!
    See trello documentation for log file naming conventions.
    The server name was little more than a novelty to begin with.
    But I like the idea of critical errors being written in the second person.
    'Steve has encountered an error'
    """

    config = configparser.ConfigParser()

    #default values:
    config['server']  = {'server_log_level' : 'debug',
                         'server_name' : 'Steve',
                         'bb_com_port' : 'COM3',
                         'bb_baud_rate' : '19200'
                         }
    config_file = open(settings_file_const, 'x')
    config.write(config_file)                                                           # the new ini file is created in the root directory


def create_logger(log_file_const, log_level='DEBUG', log_name = 'a_logger_has_no_name'):
    """Creates a logger fro the server. Depends on logging module.
    Logger is created with default level set to 'debug'.
    level may be changed later by config files."""

    # Create logger
    log = logging.getLogger(log_name)
    log.setLevel(logging.DEBUG)
    fh = logging.FileHandler(log_file_const)    # file handler object for logger
    ch = logging.StreamHandler()                # create console handler

    ch.setLevel(logging.DEBUG)                  # default log levels set to debug in case config fails
    fh.setLevel(logging.DEBUG)                  # default log levels set to debug in case config fails

    #set levels from config file
    if log_level == 'DEBUG':
        ch.setLevel(logging.DEBUG)
        fh.setLevel(logging.DEBUG)
    elif log_level == 'INFO':
        ch.setLevel(logging.INFO)
        fh.setLevel(logging.INFO)
    elif log_level == 'WARNING':
        ch.setLevel(logging.WARNING)
        fh.setLevel(logging.WARNING)
    elif log_level == 'ERROR':
        ch.setLevel(logging.ERROR)
        fh.setLevel(logging.ERROR)
    elif log_level == 'CRITICAL':
        ch.setLevel(logging.CRITICAL)
        fh.setLevel(logging.CRITICAL)
    else:
        log.critical('Bad logger level set in config file. reverting to "debug" logger')
        log.setLevel(logging.DEBUG)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    log.addHandler(fh)
    log.addHandler(ch)

    return log


def load_server_config(settings_file_const, log):
    """loads a config file and applies it to the server.
    Right now it only sets the logger level, we'll add more as we go along."""

    # try to load the config file. If this fails, the server exits.
    try:
        config = configparser.ConfigParser()
        config.read(settings_file_const)
        return config
    except KeyError:
        log.critical('Config file KeyError. Check config file for missing values!')
        exit("Config file KeyError. Check config file for missing values!")


def log_dump(obj, logger=None):
    """ Dump contents of an object for debugging. If no logger is supplied as a second arg, object is dumped to console."""
    if logger is None:
        for attr in dir(obj):
            if hasattr( obj, attr ):
                print( "obj.%s = %s" % (attr, getattr(obj, attr)))
                return
    else:
        for attr in dir(obj):
            if hasattr( obj, attr ):
                logger.critical( "obj.%s = %s" % (attr, getattr(obj, attr)))
                return
