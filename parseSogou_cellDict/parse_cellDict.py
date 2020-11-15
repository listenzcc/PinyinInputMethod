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

    def _forward(self, step=2):
        # Read self.rawdata,
        # Read the next [step] bytes and return the unpacked bytes

        # The [step] value should be even
        assert(step % 2 == 0)

        # Read one pair of bytes
        if step == 2:
            self.pos += step
            return struct.unpack(self.format, self.rawdata[self.pos-2:self.pos])[0]

        # Read several pair of bytes
        grouped_each_pairBytes = [self.rawdata[self.pos+i*2:self.pos+i*2+2]
                                  for i in range(step >> 1)]
        self.pos += step
        return [struct.unpack(self.format, e)[0] for e in grouped_each_pairBytes]

    def _str(self, lst):
        # Convert lst into string
        if not isinstance(lst, type([])):
            lst = [lst]
        string = ''.join([chr(e) for e in lst])
        string = string.replace('\x00', '')
        return string

    def pipeline(self):
        # Pipeline of reading the bytes
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
        # Starts with 0x130
        self.pos = 0x130

        # Read infos in order
        self.Name = self._str(self._forward(0x330-self.pos))
        self.Type = self._str(self._forward(0x540-self.pos))
        self.Description = self._str(self._forward(0xd40-self.pos))
        self.Example = self._str(self._forward(self.pinYin_offset-self.pos))

    def read_pinYin_table(self):
        # Read pinYin table of the .scel file
        # Starts with self.pinYin_offset
        self.pos = self.pinYin_offset

        # Will generate pinYin table and count,
        # table: table of pinYins,
        # count: count of pinYins
        self.pinYin_table = dict()
        self.pinYin_count = dict()

        # First 4 bytes is fixed for check
        self._forward(4)

        # Read until reach self.ciZu_offset
        # Structure is (idx x 2, length x 2, pinYin x length)
        while self.pos < self.ciZu_offset:
            # idx
            idx = self._forward()
            # length of pinYin bytes
            length = self._forward()
            # pinYin
            pinYin = self._str(self._forward(length))
            # pinYin = self.byte2str(self.rawdata[self.pos:self.pos+length])
            # self.pos += length
            # Record
            self.pinYin_table[idx] = pinYin
            self.pinYin_count[pinYin] = 0

        return self.pinYin_table

    def get_pinYin(self, idx, count=False):
        # Check out the [idx] of the pinYin table,
        # Count getting times if [count] is True
        if idx not in self.pinYin_table:
            return '--'

        pinYin = self.pinYin_table[idx]
        if count:
            self.pinYin_count[pinYin] += 1

        return pinYin

    def read_ciZu(self):
        # Read ciZu in the .scel file
        # Starts with self.ciZu_offset
        self.pos = self.ciZu_offset

        # Will generate words list,
        # each word is three elements tuple: (count, pinYin, ciZu)
        self.words = []

        # Read until reach the end of the file
        # Structure is
        while self.pos < len(self.rawdata):
            # count of ciZu with the same pinYin
            num = self._forward()
            # length of pinYin bytes
            length = self._forward()
            # pinYin
            pinYin_idxs = self._forward(length)
            pinYin = ''.join([self.get_pinYin(idx, count=True)
                              for idx in pinYin_idxs])

            # Read the ciZu words
            for _ in range(num):
                # length of the word bytes
                length = self._forward()
                # word
                word = self._str(self._forward(length))
                # length of extend bytes
                length = self._forward()
                # word count is in the first 2 bytes of extend
                extend = self._forward(length)
                count = extend[0]
                # Record
                self.words.append((count, pinYin, word))

        return self.words


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
celldict.words

# %%
celldict.pinYin_count

# %%
