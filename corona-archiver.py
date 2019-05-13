# !/usr/bin/env python
# -*- coding:utf-8 -*-
import logging
import os
import pprint
import struct
import sys


class CoronaArchiver:
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

    def __repr__(self):
        return pprint.pformat(vars(self))

    def pack(self, input_dir, output_file):
        self.__input_dir = input_dir

        with open(output_file, 'wb+') as f:
            self.stream = f

            files = [name for name in os.listdir(self.__input_dir) if os.path.isfile(self.__input_dir + name)]
            self.metadata['length'] = len(files)

            # Write metadata
            self.stream.write(self._MAGIC_NUMBER_HEADER)
            self.stream.write(struct.pack('i', 1))  # revision
            self.stream.write(struct.pack('i', 0))  # data_offset_start: temp writing as file content is not defined yet
            self.stream.write(struct.pack('i', self.metadata['length']))  # length: number of index entries

            # Write index entries
            for filename in files:
                padding_length = self._padding_length(len(filename), 'index')
                offset = 1337  # temporary writing as data offset is not known yet
                self.stream.write(struct.pack('iii', self._MAGIC_NUMBER_INDEX, offset, len(filename)))
                self.stream.write(filename.encode('utf-8'))
                self._write_padding(padding_length)

            # Update data_offset_start
            tell = self.stream.tell()
            data_offset_start = self.stream.tell() - 12  # tell() - tell() after writing data_offset_start value
            self.stream.seek(8, 0)
            self.stream.write(struct.pack('i', data_offset_start))
            self.stream.seek(tell, 0)

            # Write data entries
            for filename in files:
                with open(self.__input_dir + filename, 'rb') as f_append:
                    length = os.path.getsize(self.__input_dir + filename)
                    padding_length = self._padding_length(length, 'data')
                    nxt = length + 4 + padding_length

                    self.index[filename] = int(self.stream.tell())

                    self.stream.write(struct.pack('iii', self._MAGIC_NUMBER_DATA, nxt, length))  # Write data header
                    self.stream.write(f_append.read())  # Write file content
                    self._write_padding(padding_length)  # Write padding

            # Write end
            self.stream.write(self._MAGIC_NUMBER_END)
            self.stream.write(struct.pack('i', 0))

            # Replace temporary "data_offset" values with final ones
            self._write_finalize(files)

        print("File {} successfully created.".format(output_file))

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

            # Jump to next section (jump over padding)
            while struct.unpack('b', f.read(1))[0] != self._MAGIC_NUMBER_DATA:
                pass
            f.seek(-1, 1)

            # Read data entries
            self._read_data_idx()

            print("Extraction done.")

    @staticmethod
    def _padding_length(length, type):
        """ 
            Padding to fill multiple of 4 length
            Padding for index entries and data entries are different :
                - index: if length is multiple of 4, no padding
                - data: if length is multiple of 4, add 4*0x00 padding
        """
        padding = (length + (4 - length % 4)) - length
        if type == 'data':
            padding = padding if padding < 4 else 0

        return padding

    # PACKING

    def _write_finalize(self, files):
        self.stream.seek(16, 0)

        self.stream.flush()

        for filename in files:
            padding_length = self._padding_length(len(filename), 'index')

            dtype, = struct.unpack('i', self.stream.read(4))

            self.stream.seek(self.stream.tell())  # fix Windows bug: http://bugs.python.org/issue1521491
            self.stream.write(struct.pack('i', self.index[filename]))  # Write new offset value
            self.stream.seek(self.stream.tell())  # fix Windows bug: http://bugs.python.org/issue1521491

            length, = struct.unpack('i', self.stream.read(4))
            self.stream.read(length + padding_length)

    def _write_padding(self, padding):
        for i in range(padding):
            self.stream.write(b'\x00')

    # UNPACKING

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
            logging.warn("This unpacker is intended for use on Corona Revision 1, it may not work on revision {}.".format(revision))

        # Read data start offset
        data_offset_start, = struct.unpack('i', self.stream.read(4))
        self.metadata['data_offset_start'] = int(data_offset_start + self.stream.tell())

        # Read number of index entries
        length, = struct.unpack('i', self.stream.read(4))
        self.metadata['length'] = length

    def _read_index_entry(self, can_read):
        dtype, offset, length = struct.unpack('iii', self.stream.read(12))

        self.index[offset] = self.stream.read(length)
        logging.debug("{} {} {} {}".format(dtype, offset, length, self.index[offset]))

        self._read_to_next_entry(self._MAGIC_NUMBER_INDEX, can_read)

    def _read_data_entry(self, offset, filename, read_index, can_read):

        if read_index:
            self.stream.seek(offset)

        dtype, nxt, length = struct.unpack('iii', self.stream.read(12))
        content = self.stream.read(length)
        logging.debug("{} {} {} {} {}".format(dtype, nxt, length, offset, filename))

        self._write_data_entry(content, offset if offset else self.stream.tell(), filename)

        if not read_index:
            self._read_to_next_entry(self._MAGIC_NUMBER_DATA, can_read)

    def _read_data_idx(self):
        """ Read data entries by index offset values """
        for offset, filename in self.index.items():
            self._read_data_entry(offset, filename, True, True)

    def _read_data_stream(self):
        """ Read data entries by file stream flow """
        while self.stream.tell() < self.metadata['file_size']:
            self._read_data_entry(None, None, False, True)

    def _read_to_next_entry(self, entry_type, can_read=True):

        while can_read and struct.unpack('b', self.stream.read(1))[0] != entry_type:
            if self.stream.tell() + 1 >= self.metadata['file_size']:
                self.stream.seek(0, 2)
                return

        self.stream.seek(-1, 1)

    def _write_data_entry(self, content, offset, filename):
        new_filename = str(filename, 'utf-8')
        if not filename:
            new_filename = "file-" + str(offset) + ".extracted.lu"

        with open(self.__output_dir + new_filename, "wb") as f:
            f.write(content)
            logging.info("File {} extracted to {}".format(new_filename, self.__output_dir))


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, format='%(asctime)s:%(levelname)-8s %(message)s')

    if len(sys.argv) != 4:
        print("Usage: ")
        print("\tpacking:\tcorona-archiver.py -p 'input_dir' 'output_file'")
        print("\tunpacking:\tcorona-archiver.py -u 'input_file' 'output_dir'")
        sys.exit(1)

    method = sys.argv[1]
    input = sys.argv[2]
    output = sys.argv[3]

    archiver = CoronaArchiver()

    if method == '-p':
        archiver.pack(input_dir=os.path.join(input, ''), output_file=output)
    elif method == '-u':
        archiver.unpack(input_file=input, output_dir=os.path.join(output, ''))
    else:
        print("Invalid method")
