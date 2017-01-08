# !/usr/bin/env python
# -*- coding:utf-8 -*-
import argparse
import os
import pprint
import struct
import logging


class CoronaArchive:
    _MAGIC_NUMBER_HEADER = b'\x72\x61\x63\x01'  # ASCII = rac.
    _MAGIC_NUMBER_INDEX = 1
    _MAGIC_NUMBER_DATA = 2
    _MAGIC_NUMBER_END = b'\xFF\xFF\xFF\xFF'

    stream = None
    metadata = {}
    index = {}
    data = {}

    __input_dir = ""
    __output_dir = ""

    def __init__(self):
        pass

    def pack(self, input_dir, output_file):
        self.__input_dir = input_dir
        logging.exception(NotImplementedError)

    def unpack(self, input_file, output_dir):
        self.__output_dir = output_dir

        with open(input_file, 'rb') as f:
            self.stream = f

            # Read metadata
            self.metadata['file_path'], self.metadata['file_name'] = os.path.split(input_file)
            self.metadata['file_size'] = os.path.getsize(input_file)
            self._read_metadata()

            # Read index entries
            for i in range(0, self.metadata['length']):
                can_read = (i != self.metadata['length'] - 1)
                self._read_index_entry(can_read)

            # Jump to next section
            while struct.unpack('b', f.read(1))[0] != self._MAGIC_NUMBER_DATA:
                pass
            f.seek(-1, 1)

            # Read data entries
            self._read_data_stream()

            print "Extraction done."

    def _read_metadata(self):
        # Read header
        header = self.stream.read(4)
        self.metadata['header'] = header
        if header != self._MAGIC_NUMBER_HEADER:
            logging.error("Incorrect file type. Must be a *.car (Corona Archive) file type.")
            exit(1)

        # Read archive version
        revision, = struct.unpack('i', self.stream.read(4))
        self.metadata['revision'] = revision
        if revision != 1:
            logging.warn("This unpacker is intended for use on Corona Revision 1, it may not work on revision", revision, ".")

        # Read data start offset
        data_offset_start, = struct.unpack('i', self.stream.read(4))
        self.metadata['data_offset_start'] = int(data_offset_start + self.stream.tell())

        # Read number of index entries
        length, = struct.unpack('i', self.stream.read(4))
        self.metadata['length'] = length

    def _read_index_entry(self, can_read):
        dtype, offset, length = struct.unpack('iii', self.stream.read(12))

        self.index[offset] = self.stream.read(length)
        logging.debug(dtype, offset, length, self.index[offset])

        self._read_to_next_entry(self._MAGIC_NUMBER_INDEX, can_read)

    def _read_data_entry(self, offset, filename, read_index, can_read):

        if read_index:
            self.stream.seek(offset)

        dtype, nxt, length = struct.unpack('iii', self.stream.read(12))
        content = self.stream.read(length)
        logging.debug(dtype, nxt, length, offset, filename)

        self._write_data_entry(content, offset if offset else self.stream.tell(), filename)

        if not read_index:
            self._read_to_next_entry(self._MAGIC_NUMBER_DATA, can_read)

    def _read_data_idx(self):
        # Read entries by offset values
        for offset, filename in self.index.items():
            self._read_data_entry(offset, filename, True, True)

    def _read_data_stream(self):
        # Read entries by stream flow
        while self.stream.tell() < self.metadata['file_size']:
            self._read_data_entry(None, None, False, True)

    def _read_to_next_entry(self, entry_type, can_read=True):

        while can_read and struct.unpack('b', self.stream.read(1))[0] != entry_type:
            if self.stream.tell() + 1 >= self.metadata['file_size']:
                self.stream.seek(0, 2)
                return

        self.stream.seek(-1, 1)

    def _write_data_entry(self, content, offset, filename):
        new_filename = filename
        if not filename:
            new_filename = "file-" + str(offset) + ".extracted.lu"

        with open(self.__output_dir + new_filename, "wb") as f:
            f.write(content)
            logging.info("File", new_filename, "extracted to", self.__output_dir)

    def __repr__(self):
        return pprint.pformat(vars(self))

# def command_line(sys_args):
#     parser = argparse.ArgumentParser(description='Corona Archive Packer/Unpacker')
#     parser.add_argument('--version', action='version', version='%(prog)s ' + MDAP_LIB_VERSION)
#     parser.add_argument('-d', action='store_true', help='send ANT-SEARCH discovery packet to multicast')
#     parser.add_argument('-i', metavar='iface_ip', help='the interface used to listen and send MDAP packets')
#     parser.add_argument('-t', metavar='target', help='the target device (ant_id, ip)')
#     parser.add_argument('-m', metavar='method', choices=['info', 'exec'], help='the method to call (%(choices)s)')
#     parser.add_argument('-c', metavar='command', help='the command to execute', nargs='*')
#     parser.add_argument('-u', metavar='user')
#     parser.add_argument('-p', metavar='password')
#     parser.add_argument('-v', '--verbose', action='count', help="add more 'v' for more verbose (up to 3)")
#
#     args = parser.parse_args(sys_args)
#
#     print ''
#
#     if args.verbose:
#         logging.getLogger().setLevel(__log_levels.get('-' + ('v' * args.verbose), logging.WARNING))
#
#     mdap = MDAP(args.i)
#     if args.d:
#         mdap.discover()
#         time.sleep(1)
#         print(mdap.ants)
#     mdap.set_target(args.t)
#     if 'info' == args.m:
#         mdap.info(args.u, args.p)
#         time.sleep(1)
#         print(mdap.ants)
#     if 'exec' == args.m:
#         mdap.exec_cmd(' '.join(args.c), args.u, args.p)
#         time.sleep(1)

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, format='%(asctime)s:%(levelname)-8s %(message)s')

    archive = CoronaArchive()
    archive.unpack("c:\\Users\\BuRner\\My Code\\FamilyQuizz\\scrapers\\trivia_quiz\\resource.car", "c:\\Users\\BuRner\\Downloads\\temp1\\")

    print archive.metadata
    print archive.index
    # command_line(sys.argv[1:])
