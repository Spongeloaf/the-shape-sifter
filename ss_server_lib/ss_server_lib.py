# Third party imports
import multiprocessing
import time
from os.path import isfile
import numpy as np
import sqlite3

# first party imports. Safe to use from x import *
import shape_sifter_tools as ss
import shape_sifter_clients
import bb_client_lib as bb
import taxidermist_lib

""" This file contains all of the shape sifter server specific functions.
Common functions and classes used by more than the server are stored elsewhere."""

# TODO: Change this library to create PartInstance objects when it pulls parts from the DB. Right now we simply get a string, and slice it.
# TODO: Properly plan belt buckle timeouts and status changes


class server_init:
    """Write something here"""

    def __init__(self):
        # declarations and initializations. All objects ending with _const are NOT to be modified at run time!
        self.server_settings_file_const = 'settings.ini'
        self.server_log_file_const = 'log\\log_server.txt'
        self.server_db_fname_const = 'db\\shape_sifter.sqlite'
        self.server_db_template_const = 'db\\shape_sifter_template.sqlite'
        self.part_log_fname_const = 'log\\part_log.txt'
        self.active_part_table_const = ('active_part_db',)
        self.prev_id = ''
        self.jobs = []

        # create logger, default debug level. Level will be changed once config file is loaded
        self.logger = ss.create_logger(self.server_log_file_const, 'DEBUG')

        # TODO: Move this somewhere else! Make a function out of it along with the next block below
        # if config file doesn't exist, create one. Defaults are in shape_sifter_tools.py
        if not isfile(self.server_settings_file_const):
            self.logger.info("config file doesn't exist. Creating...")
            ss.create_server_config(self.server_settings_file_const)

        # load config file and assign values.
        # TODO: Turn this into a function that verifies the settings and returns an object. It should also handle key exceptions
        self.server_config = ss.load_server_config(self.server_settings_file_const, self.logger)
        self.server_log_level = self.server_config['server']['log_level']
        self.server_bb_ack_timeout = self.server_config['server']['bb_ack_timeout']

        self.taxi_log_level = self.server_config['cf']['log_level']
        self.mtm_log_level = self.server_config['mtm']['log_level']
        self.cf_log_level = self.server_config['cf']['log_level']

        self.bb_com_port = self.server_config['bb']['com_port']
        self.bb_baud_rate = self.server_config['bb']['baud_rate']
        self.bb_skip_handshake = self.server_config['bb']['skip_handshake']
        self.bb_log_level = self.server_config['bb']['log_level']
        self.bb_timeout = self.server_config['bb']['timeout']

        # replace logger with level set by config file
        self.logger = ss.create_logger(self.server_log_file_const, self.server_log_level, 'server')
        self.part_log = ss.create_logger(self.part_log_fname_const, 'DEBUG', 'part_log')

        # the primary SQLite table used for tracking active parts. Will be iterated each loop to update part status.
        self.active_part_db = setup_active_part_table(self.server_db_fname_const, self.server_db_template_const, self.logger)

        # used by all primary DB functions, such as the main active part db iterator and most insert/update functions
        self.primary_curr = self.active_part_db.cursor()

        # used when the primary cursor is already in use. Typically inside loops made by the primary cursor.
        self.secondary_curr = self.active_part_db.cursor()

        # pipe from taxidermist to BB
        self.pipe_bb_recv_taxi, self.pipe_taxi_send_bb = multiprocessing.Pipe(duplex=False)

        # start taxidermist
        self.pipe_taxi_recv_server, self.pipe_server_send_taxi = multiprocessing.Pipe(duplex=False)
        self.pipe_server_recv_taxi, self.pipe_taxi_send_server = multiprocessing.Pipe(duplex=False)
        self.p1 = multiprocessing.Process(target=taxidermist_lib.taxidermist, args=(self.pipe_taxi_recv_server, self.pipe_taxi_send_server, self.pipe_taxi_send_bb, self.taxi_log_level))
        self.jobs.append(self.p1)
        self.taxi = self.p1.start()
        self.logger.info('taxidermist started')

        # Start mtmind simulator
        self.pipe_mtm_recv_server, self.pipe_server_send_mtm = multiprocessing.Pipe(duplex=False)
        self.pipe_server_recv_mtm, self.pipe_mtm_send_server = multiprocessing.Pipe(duplex=False)
        self.p2 = multiprocessing.Process(target=shape_sifter_clients.mt_mind_sim, args=(self.pipe_mtm_recv_server, self.pipe_mtm_send_server, self.mtm_log_level))
        self.jobs.append(self.p2)
        self.mtm = self.p2.start()
        self.logger.info('mt_mind_sim started')

        # start classifist
        self.pipe_classifist_recv, self.pipe_server_send_cf = multiprocessing.Pipe(duplex=False)
        self.pipe_server_recv_cf, self.pipe_classifist_send = multiprocessing.Pipe(duplex=False)
        self.p3 = multiprocessing.Process(target=shape_sifter_clients.classifist, args=(self.pipe_classifist_recv, self.pipe_classifist_send, self.server_db_fname_const, self.cf_log_level))
        self.jobs.append(self.p3)
        self.classifist = self.p3.start()
        self.logger.info('classifist started')

        # start belt buckle
        self.pipe_bb_recv, self.pipe_server_send_bb = multiprocessing.Pipe(duplex=False)
        self.pipe_server_recv_bb, self.pipe_bb_send = multiprocessing.Pipe(duplex=False)
        self.p4 = multiprocessing.Process(target=bb.belt_buckle_client,
                                          args=(self.pipe_bb_recv, self.pipe_bb_send,
                                                self.pipe_bb_recv_taxi,
                                                self.bb_com_port, self.bb_baud_rate,
                                                self.bb_log_level, self.bb_skip_handshake))
        self.jobs.append(self.p4)
        self.bb = self.p4.start()
        self.logger.info('belt buckle started')

        # # start the SUIP_er_simple
        # pipe_suip_recv, pipe_server_send_suip = multiprocessing.Pipe(duplex=False)
        # pipe_server_recv_suip, pipe_suip_send = multiprocessing.Pipe(duplex=False)
        # p5 = multiprocessing.Process(target=shape_sifter_clients.suip_er_simple, args=())
        # jobs.append(p5)
        # dev_mule = p5.start()
        # logger.info('SUIP started')

        # start the SUIP
        self.pipe_suip_recv, self.pipe_server_send_suip = multiprocessing.Pipe(duplex=False)
        self.pipe_server_recv_suip, self.pipe_suip_send = multiprocessing.Pipe(duplex=False)
        self.p5 = multiprocessing.Process(target=shape_sifter_clients.suip, args=(self.pipe_suip_recv, self.pipe_suip_send, self.server_db_fname_const))
        self.jobs.append(self.p5)
        self.suip = self.p5.start()
        self.logger.info('SUIP started')


class server_mode:
    """Server video_source object. Stores attributes used to control the state of the server."""

    def __init__(self):
        self.iterate_active_part_db = False
        self.check_taxi = False
        self.check_mtm = False
        self.check_cf = False
        self.check_bb = False


def iterate_active_part_db(server: server_init):
    """
    Iterate active part db. Once per main server loop we check for actionable statuses on all current parts.
    Actions are taken where necessary. Each If statement below represents and actionable status.
    see the documentation on Trello for a complete list of what all the statuses mean.

    row[1] = instance_id
    row[2] = capture_time
    row[3] = part_number
    row[6] = part_
    row[8] = bin assignment
    row[9] = server status
    row[10] = bb_status
    row[11] = serial_string
    row[12] = bb_timeout

    :param primary_curr: sql cursor
    :param secondary_curr: sql cursor
    :return: none
    """

    for row in server.primary_curr.execute("SELECT * FROM active_part_db"):

        # row_part: ss.PartInstance = creat_obj_from_sql_row(row)

        # server status = new; the part was just received from the taxidermist. Send it to the MTM
        if row[9] == 'new':
            taxi_done_part = ss.part_instance(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], 'wait_mtm', row[10], row[11])  # TODO make this work with dynamic changes in column counts!
            taxi_done_part_tuple = (taxi_done_part.server_status, taxi_done_part.instance_id,)
            server.pipe_server_send_mtm.send(taxi_done_part)
            server.secondary_curr.execute("UPDATE active_part_db SET server_status=? WHERE instance_id=?", taxi_done_part_tuple)
            server.active_part_db.commit()

        # server status = mtm_done; the part was returned frm the MTMind, send it to the classifist.
        if row[9] == 'mtm_done':
            mtm_done_part = ss.part_instance(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], 'wait_cf', row[10], row[11])  # TODO make this work with dynamic changes in column counts!
            mtm_done_part_tuple = (mtm_done_part.server_status, mtm_done_part.instance_id,)
            server.pipe_server_send_cf.send(mtm_done_part)
            server.secondary_curr.execute("UPDATE active_part_db SET server_status=? WHERE instance_id=?", mtm_done_part_tuple)
            server.active_part_db.commit()

        # server_status = cf_done; the part was returned from the classifist. Send the bin assignment to the belt buckle.
        if row[9] == 'cf_done':
            cf_done_packet = ss.bb_packet(command='B', argument=row[8], payload=row[1], type='BBC')
            if cf_done_packet.status_code == '200':
                server.pipe_server_send_bb.send(cf_done_packet)

                # make a time stamp so we can resend the packet if we don't get a reply in 50ms
                capture_time = time.monotonic()

                cf_done_part_tuple = ('wait_bb', cf_done_packet.serial_string, capture_time, row[1],)
                server.secondary_curr.execute("UPDATE active_part_db SET server_status=?, serial_string=?, capture_time=? WHERE instance_id=?", cf_done_part_tuple)
                server.active_part_db.commit()
            else:
                server.logger.error(
                    'Bad BbPacket when processing "cf_done" while iterating part table. Packet:{}'.format(vars(cf_done_packet)))

        # checks for any parts that have not been acknowledged by the belt buckle
        if row[9] == 'wait_bb':
            if (time.monotonic() - row[2]) > row[12]:
                print('BB timeout: ({} - {}) > {}'.format(time.monotonic(), row[2], row[12]))
                wait_bb_packet = ss.bb_packet(serial_string=row[11])
                if wait_bb_packet.status_code == '200':
                    server.pipe_server_send_bb.send(wait_bb_packet)
                    new_timeout = row[12] * 2
                    wait_bb_packet_tuple = (new_timeout, row[1])
                    server.secondary_curr.execute("UPDATE active_part_db SET bb_timeout=? WHERE instance_id=?", wait_bb_packet_tuple)
                    server.active_part_db.commit()
                else:
                    server.logger.error(
                        'Bad BbPacket when processing "wait_bb" while iterating part table. Packet:{}'.format(vars(wait_bb_packet)))

        if row[9] == 'bb_done':
            # read_part = ss.PartInstance(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11])
            pass
            # TODO:
            # set server_status to wait_sort

        if row[9] == 'sort_done':
            # read_part = ss.PartInstance(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11])
            pass
            # TODO:
            # send to log
            # clear row from active part DB

        if row[9] == 'lost':
            # read_part = ss.PartInstance(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11])
            pass
            # TODO:
            # send to log
            # clear row from active part DB


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

            # stops the belt
            server.pipe_server_recv_suip.fileno()
        except AttributeError:
            server.logger.error("Attribute Error in check_suip(). See dump on next line")
            server.logger.error("{0}".format(suip_command))


def check_taxi(server):
    """Checks the taxidermist for parts"""
    # checks if the taxidermist has anything for us. Sends the part to the MTM and the BB
    if server.pipe_server_recv_taxi.poll(0) == True:
        taxi_read_part = server.pipe_server_recv_taxi.recv()
        taxi_read_part_tuple = ss.create_sql_part_tuple(taxi_read_part)
        server.primary_curr.execute('INSERT INTO active_part_db VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?,?)', taxi_read_part_tuple)
        server.active_part_db.commit()


def check_mtm(server):
    """Checks the MT mind for parts"""
    # checks if the mtm pipe has something yet, if so, read that shit and do stuff
    if server.pipe_server_recv_mtm.poll(0) == True:
        mtm_read_part = server.pipe_server_recv_mtm.recv()
        # mtm_read_part_tuple = ss.create_sql_part_tuple(mtm_read_part)
        mtm_read_part_tuple = ('{0}'.format(mtm_read_part.part_number),
                               '{0}'.format(mtm_read_part.category_number),
                               '{0}'.format(mtm_read_part.category_name),
                               '{0}'.format(mtm_read_part.server_status),
                               '{0}'.format(mtm_read_part.instance_id)
                               )
        server.primary_curr.execute("UPDATE active_part_db SET part_number=?,category_number=?,category_name=?,server_status=? WHERE instance_id=?", mtm_read_part_tuple)
        server.active_part_db.commit()


def check_cf(server):
    """Checks the classifist for parts"""
    # checks if the classifist pipe has something yet, if so, read that shit and do stuff
    if server.pipe_server_recv_cf.poll(0) == True:
        cf_read_part: ss.part_instance = server.pipe_server_recv_cf.recv()
        cf_read_part_tuple = (cf_read_part.bin_assignment, cf_read_part.server_status, cf_read_part.instance_id)
        server.primary_curr.execute("UPDATE active_part_db SET bin_assignment=?, server_status=? WHERE instance_id=?", cf_read_part_tuple)
        server.active_part_db.commit()
        # logger.debug(active_curr.execute("SELECT * FROM active_part_db WHERE instance_id=?", cf_read_part_tuple))


def check_bb(server):
    """Checks the belt buckle for messages"""
    # TODO: Add support for all the response codes below. Remove all the PASS commands and replace them with proper commands
    if server.pipe_server_recv_bb.poll(0):
        bb_read_part: ss.bb_packet = server.pipe_server_recv_bb.recv()
        if bb_read_part.status_code == '200':

            # TEL commands notify the server that...
            if bb_read_part.type == 'TEL':

                # ...a part has been sorted. Remove it from the active_part_db.
                if bb_read_part.command == 'C':
                    bb_read_part_tuple = (bb_read_part.payload,)
                    for rows in server.primary_curr.execute("SELECT FROM active_part_db WHERE instance_id=?", bb_read_part_tuple):
                        server.part_log("part:{}, color:{}, bin:{}".format(rows[3],rows[6],rows[8]))
                    server.primary_curr.execute("DELETE FROM active_part_db WHERE instance_id=?", bb_read_part_tuple)

                # ...a part has gone off the end of the belt
                if bb_read_part.command == 'F':
                    bb_read_part_tuple = (bb_read_part.payload, )
                    for rows in server.primary_curr.execute("SELECT FROM active_part_db WHERE instance_id=?", bb_read_part_tuple):
                        server.part_log("part:{}, color:{}, bin: 0 - missed assigned bin".format(rows[3],rows[6]))
                    server.primary_curr.execute("DELETE FROM active_part_db WHERE instance_id=?", bb_read_part_tuple)

                # ...a handshake has been received
                if bb_read_part.command == 'H':
                    pass

                # ...the belt buckle has requested to download the bin config
                if bb_read_part.command == 'D':
                    pass

            # ACK commands inform the server that a previous BBC command sent to the BB was received, understood, and executed. Any errors will be indicated by the response code
            if bb_read_part.type == 'ACK':

                # the previous BBC command was executed correctly. Update the active_part_DB
                if bb_read_part.response == '200':
                    # ...a part has been sorted
                    if bb_read_part.command == 'B':
                        bb_read_part_tuple = ('bb_done', bb_read_part.payload)
                        server.primary_curr.execute("UPDATE active_part_db SET server_status=? WHERE instance_id=?", bb_read_part_tuple)
                        server.active_part_db.commit()

                else:
                    server.logger.error("slib.check_bb failed. response code = {}. Packet:{}".format(bb_read_part.response, vars(bb_read_part)))

        else:
            server.logger.error("A packet received from by the check_BB function has a bad status code. {}".format(vars(bb_read_part)))


def setup_active_part_table(db_fname, db_template_fname, logger):
    """Creates an SQlite table in memory for tracking parts on the belt and returns this table to the caller.
    It creates an instance of a part class and uses it's __dict__ keys to create columns in the table

    # TODO: Add table checks! right now we're only checking if the file exists!
    """

    # if sqlite file doesn't exist, create it from template. Template is set in declarations and initializations section of the server.py.
    if not isfile(db_fname):
        logger.info("{0} not found. Creating a new one.....".format(db_fname))
        copyfile(db_template_fname, db_fname)

    # Converts np.array to TEXT when inserting
    sqlite3.register_adapter(np.ndarray, adapt_np_array_for_sql)

    # Converts TEXT to np.array when selecting
    sqlite3.register_converter("array", convert_sql_text_to_array)

    # create the new active part table in the db, using list comprehension to create column names from attributes in the part class.
    active_part_db = sqlite3.connect(db_fname)
    sqlcurr = active_part_db.cursor()
    sqlcurr.execute("DROP TABLE IF EXISTS active_part_db")
    active_part_db.commit()
    sqlcurr.execute("CREATE TABLE IF NOT EXISTS active_part_db (ID INTEGER PRIMARY KEY) ")

    # use list comprehension and an instance of a part class to populate the database with columns of matching types.
    part_dummy = ss.part_instance()
    active_part_columns: List[str] = [i for i in part_dummy.__dict__.items()]  # holy fuck list comprehension is cool

    for i in active_part_columns:

        # These return True if the items() in part_dummy are floats or ints.
        is_float = isinstance(i[1], float)
        is_int = isinstance(i[1], int)

        # TODO: Add support for NP arrays for part images in the DB
        # is_blob = isinstance(i[1], numpy array)

        if is_float:
            sqlcurr.execute("ALTER TABLE active_part_db ADD COLUMN {0} REAL".format(i[0]))

        elif is_int:
            sqlcurr.execute("ALTER TABLE active_part_db ADD COLUMN {0} INTEGER".format(i[0]))

        # We assume we are storing strings if not explicitly storing anything else like float or int.
        else:
            sqlcurr.execute("ALTER TABLE active_part_db ADD COLUMN {0} TEXT".format(i[0]))

    active_part_db.commit()
    return active_part_db


def adapt_np_array_for_sql(image_array):
    """
    http://stackoverflow.com/a/31312102/190597 (SoulNibbler)

    converts an np array to a text string to store in SQL
    """
    out = io.BytesIO()
    np.save(out, image_array)
    out.seek(0)
    return sqlite3.Binary(out.read())


def convert_sql_text_to_array(text):
    """
    http://stackoverflow.com/a/31312102/190597 (SoulNibbler)

    converts a text string, stored in SQL to an np array
    """
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)
