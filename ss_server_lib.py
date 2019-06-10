# Third party imports
import time
import multiprocessing
from typing import List

# first party imports. Safe to use from x import *
import ss_classes
from ss_classes import ServerInit
import shape_sifter_tools.shape_sifter_tools as ss
from belt_buckle_client.belt_buckle_client import BbClient

""" This file contains all of the shape sifter server specific classes and functions.
Common functions and classes used by more than the server are stored elsewhere."""


# TODO: Properly plan belt buckle timeouts

class Server:
    def __init__(self, init: ServerInit, bb: BbClient):
        self.params = init
        self.part_list = []
        self.sort_log = ss.create_logger(self.params.server_sort_log_file_const, 'INFO', "sort_log")
        self.logger = self.params.logger
        self.bb = bb
        self.pipes = init.pipes


    def iterate_part_list(self):
        """
        Iterate active part db. Once per main server loop we check for actionable statuses on all current parts.
        Actions are taken where necessary. Each If statement below represents and actionable status.
        see the documentation on Trello for a complete list of what all the statuses mean.

        :param self: server init object
        :return: none
        """

        # An alias for the part list which gives us type hinting.
        plist: List[ss_classes.PartInstance] = self.part_list

        # loop through the part list checking for status codes that demand action.
        # There are no "continue" statements on the bb_status checks because
        # we may also want to take action based on server status codes too.
        for part in plist:

            # checks for any parts that were sorted by the belt buckle
            if part.bb_status == 'sorted':
                self.sort_log.info('id:{}, bin{}, cat: {}, time: {}, {}, {}, {}, {}'.format(part.instance_id, part.bin_assignment, part.category_name, part.t_taxi, part.t_mtm, part.t_cf, part.t_added, part.t_assigned))
                self.part_list.remove(part)
                part.server_status = 'removed'

            # checks for parts that have been lost by the belt buckle. A part is lost if it misses it's bin and goes off the end of the belt.
            if part.bb_status == 'lost':
                self.sort_log.info('id:{}, bin{}, cat: {}, time: {}, {}, {}, {}, {}, LOST!'.format(part.instance_id, part.bin_assignment, part.category_name, part.t_taxi, part.t_mtm, part.t_cf, part.t_added, part.t_assigned))
                self.part_list.remove(part)
                part.server_status = 'removed'

            # server status = new; the part was just received from the taxidermist. Send it to the MTM
            if part.server_status == 'new':
                self.bb.send_command_a(part.camera_offset, part.instance_id)
                self.send_mtm(part)
                continue

            # server status = mtm_done; the part was returned frm the MTMind, send it to the classifist.
            if part.server_status == 'mtm_done':
                # throw away parts that are actually just belt pictures
                if part.category_name == 'belt':
                    part.server_status = 'removed'
                    self.bb.send_command_o(part.instance_id)
                    self.logger.debug("Removed 'belt' part")
                    plist.remove(part)
                    continue
                self.send_cf(part)
                continue

            # server_status = cf_done; the part was returned from the classifist. Send the bin assignment to the belt buckle.
            if part.server_status == 'cf_done':
                if part.bb_status == 'added':
                    self.bb.send_command_b(part.bin_assignment, part.instance_id)
                continue


    def check_suip(self, mode):
        """Check for commands sent by the SUIP"""
        if self.pipes.server_recv_suip.poll(0):
            suip_command = self.pipes.server_recv_suip.recv()
            try:
                # starts the server main loop
                if suip_command.command == 'server_control_run':
                    mode.iterate_active_part_db = True
                    mode.check_taxi = True
                    mode.check_mtm = True
                    mode.check_cf = True
                    mode.check_bb = True
                    self.bb.send_command_m('1001')


                # stops the server main loop
                if suip_command.command == 'server_control_halt':
                    mode.iterate_active_part_db = False
                    mode.check_taxi = False
                    mode.check_mtm = False
                    mode.check_cf = False
                    mode.check_bb = False
                    self.bb.send_command_m('1000')

            except AttributeError:
                self.logger.error("Attribute Error in check_suip(). See dump on next line")
                self.logger.error("{0}".format(suip_command))


    def check_bb(self):
        serial_string = self.bb.check_serial()

        # nothing received
        if serial_string == '':
            return

        # bad string received
        packet = self.bb.parse_serial_string(serial_string)
        if packet.status != 'ok':
            self.logger.debug("Bad packet in check_bb(): {}".format(packet))
            return

        # string is ok
        self.bb_execute_packet(packet)


    def check_taxi(self):
        """Checks the taxidermist for parts"""
        # checks if the taxidermist has anything for us. Sends the part to the MTM and the BB
        if self.pipes.server_recv_taxi.poll(0):
            read_part: ss_classes.PartInstance = self.pipes.server_recv_taxi.recv()
            read_part.t_taxi = time.perf_counter()
            self.part_list.append(read_part)


    def check_mtm(self):
        """Checks the MT mind for parts"""
        if self.pipes.server_recv_mtm.poll(0):
            read_part: ss_classes.PartInstance = self.pipes.server_recv_mtm.recv()
            read_part.t_mtm = time.perf_counter()

            for part in self.part_list:
                if part.instance_id == read_part.instance_id:
                    part.category_name = read_part.category_name
                    part.server_status = read_part.server_status
                    return

            self.logger.debug("No part list match when calling check_mtm(). Part: {}".format(vars(read_part)))


    def check_cf(self):
        """Checks the classifist for parts"""
        if self.pipes.server_recv_cf.poll(0):
            read_part: ss_classes.PartInstance = self.pipes.server_recv_cf.recv()
            read_part.t_cf = time.perf_counter()

            for part in self.part_list:
                if part.instance_id == read_part.instance_id:
                    part.bin_assignment = read_part.bin_assignment
                    part.server_status = read_part.server_status


    def send_mtm(self, part: ss_classes.PartInstance):
        """Sends a part to the MTMind"""
        self.pipes.server_send_mtm.send(part)
        part.server_status = 'wait_mtm'


    def send_cf(self, part: ss_classes.PartInstance):
        part.server_status = 'wait_cf'
        self.pipes.server_send_cf.send(part)


    def send_part_list_to_suip(self):
        """Sends the part list to the suip"""
        self.pipes.part_list_send.send(self.part_list)


    def bb_update_part(self, packet: ss_classes.BbPacket, status: str):
        """ Takes a packet and finds a matching part in the part list and updates it's bb_status."""
        for part in self.part_list:
            if packet.payload == part.instance_id:
                part.bb_status = status
                if status == 'assigned':
                    part.t_assigned = time.perf_counter()
                    self.logger.critical('assigned {}'.format(part.instance_id))
                    return
                if status == 'added':
                    self.logger.critical('added {}'.format(part.instance_id))
                    part.t_added = time.perf_counter()
                    return

        self.logger.info('no match in update parts')

    def bb_execute_packet(self, packet: ss_classes.BbPacket):
        """ Processes incoming packets from the belt buckle"""
        # TODO: Add support for all the response codes below. Remove all the PASS commands and replace them with proper commands
        if packet.status != 'ok':
            self.logger.critical("Bad packet in check_packet(): {}".format(packet))

        # TEL commands notify the server that...
        if packet.type == 'TEL':

            # ...a part has been sorted. Remove it from the part_list.
            if packet.command == 'C':
                self.bb_update_part(packet, 'sorted')
                return

            # ...a part has gone off the end of the belt
            if packet.command == 'F':
                self.bb_update_part(packet, 'lost')
                return

            # ...a handshake has been received
            if packet.command == 'H':
                pass

            # ...the belt buckle has requested to download the bin config
            if packet.command == 'D':
                self.logger.debug('Received download command from belt buckle')
                pass

        # ACK commands inform the server that a previous BBC command sent to the BB was received, understood, and executed. Any errors will be indicated by the response code
        elif packet.type == 'ACK':

            # ...a part has been assigned to a bin
            if packet.command == 'B':
                self.bb_update_part(packet, 'assigned')
                return

            # ...a part has been added to the tracker
            if packet.command == 'A':
                self.bb_update_part(packet, 'added')
                return

            # ...a part has been removed from the tracker
            if packet.command == 'O':
                for part in self.part_list:
                    if part.instance_id == packet.payload:
                        self.part_list.remove(part)
                        return
                return

            # ...an M command has been acknowledged. We don't need to do anything.
            if packet.command == 'M':
                pass

            else:
                self.logger.error("slib.parse_serial_string failed. Invalid response to an ACK: {}".format(packet))

        else:
            self.logger.error("A packet received from by the check_BB function has a bad status code. {}".format(packet))

