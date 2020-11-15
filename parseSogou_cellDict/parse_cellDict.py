# File: parse_cellDict.py
# Aim: Parse cell dict.

# %%
import os
import struct


class SCEL_cellDict(object):
    def __init__(self, filepath):
        self.init_settings()

        with open(filepath, 'rb') as f:
            self.rawdata = f.read()

        assert(self.legal_check())

    def init_settings(self):
        # Init settings
        self.legal_head = b'\x40\x15\x00\x00\x44\x43\x53\x01\x01\x00\x00\x00'
        self.legal_pinYin_table_head = b'\x9d\x01\x00\x00'
        self.pinYin_offset = 0x1540
        self.ciZu_offset = 0x2628
        self.format = 'H'

    def byte2str(self, data, return_raw=False, use_chr=True):
        # Convert [data] into str
        if not use_chr:
            return_raw = True

        # The length of [data] should be even
        length = len(data)
        assert(length % 2 == 0)

        # Group data in each two-data pair
        grouped_each_2bytes = [data[i*2:i*2+2] for i in range(length >> 1)]

        # Decode data using [format]
        if use_chr:
            string = ''.join([chr(struct.unpack(self.format, e)[0])
                              for e in grouped_each_2bytes])
        else:
            string = [struct.unpack(self.format, e)[0]
                      for e in grouped_each_2bytes]

        # Return the string if return_raw is True,
        # otherwise, improve useability of the string
        if return_raw:
            return string
        else:
            return string.replace('\x00', '')

    def pipeline(self):
        self.read_info()
        self.read_pinYin_table()
        self.read_ciZu()

    def legal_check(self):
        # Check if the rawdata is legal
        # Legal structure is several session:
        # 1. legal_head x 12,
        # 2. ???,
        # 3. info [from 0x130 to pinYin_offset],
        # 4. pinYin_table, [from pinYin_offset to ciZu_offset],
        #                  [first 4 bytes are legal_pinYin_table_head],
        # 5. ciZu, [from ciZu_offset to end].

        return all([
            # Check legal_head
            self.rawdata[:12] == self.legal_head,
            # Check legal_pinYin_table_head
            self.rawdata[self.pinYin_offset:self.pinYin_offset +
                         4] == self.legal_pinYin_table_head,
        ])

    def read_info(self):
        # Read info of the .scel file
        self.Name = self.byte2str(self.rawdata[0x130:0x330])
        self.Type = self.byte2str(self.rawdata[0x338:0x540])
        self.Description = self.byte2str(self.rawdata[0x540:0xd40])
        self.Example = self.byte2str(self.rawdata[0xd40:self.pinYin_offset])

    def read_pinYin_table(self):
        # Read pinYin table of the .scel file
        # Will generate pinYin table
        self.pinYin_table = dict()

        # First 4 bytes is fixed for check
        pos = self.pinYin_offset + 4

        # Read until reach self.ciZu_offset
        # Structure is (idx x 2, length x 2, pinYin x length)
        while pos < self.ciZu_offset:
            # idx
            idx = struct.unpack(self.format, self.rawdata[pos:pos+2])[0]
            pos += 2
            # length of pinYin bytes
            length = struct.unpack(self.format, self.rawdata[pos:pos+2])[0]
            pos += 2
            # pinYin
            pinYin = self.byte2str(self.rawdata[pos:pos+length])
            pos += length
            # Record
            self.pinYin_table[idx] = pinYin

        return self.pinYin_table

    def get_pinYin(self, idx):
        # Check out the [idx] of the pinYin table
        return self.pinYin_table.get(idx, '--')

    def read_ciZu(self):
        # Read ciZu in the .scel file
        self.main_table = []
        pos = self.ciZu_offset
        while pos < len(self.rawdata):
            # count of ciZu using the pinYin
            num = struct.unpack(self.format,
                                self.rawdata[pos:pos+2])[0]
            num = int(num)
            pos += 2
            # length of pinYin bytes
            length = struct.unpack(self.format,
                                   self.rawdata[pos:pos+2])[0]
            pos += 2
            # pinYin
            pinYin_idxs = self.byte2str(
                self.rawdata[pos:pos+length], use_chr=False)
            pinYin = ''.join([self.get_pinYin(idx) for idx in pinYin_idxs])
            pos += length

            # Read the ciZu words
            for _ in range(num):
                # length of the word bytes
                length = struct.unpack(self.format,
                                       self.rawdata[pos:pos+2])[0]
                pos += 2
                # word
                word = self.byte2str(self.rawdata[pos:pos+length])
                pos += length
                # length of extend
                length = struct.unpack(self.format,
                                       self.rawdata[pos:pos+2])[0]
                pos += 2
                # word count is in the first 2 bytes of extend
                count = struct.unpack(self.format,
                                      self.rawdata[pos:pos+2])[0]
                count = int(count)
                pos += length
                # Record
                self.main_table.append((count, pinYin, word))

        return self.main_table


# %%
# File settings
scel_path = os.path.join(os.path.dirname(__file__),
                         '..',
                         'cellDicts',
                         '计算机词汇大全【官方推荐】.scel')

celldict = SCEL_cellDict(scel_path)
celldict.pipeline()

# %%
(celldict.Name,
 celldict.Type,
 celldict.Description,
 celldict.Example)

# %%
celldict.pinYin_table

# %%
celldict.main_table

# %%
