# File: parse_cellDict.py
# Aim: Parse cell dict.

# %%
import json
import os
import pandas as pd
import struct
import time


class SCEL_cellDict(object):
    def __init__(self, filepath, pinYin_count=dict()):
        self.init_settings()

        with open(filepath, 'rb') as f:
            self.rawdata = f.read()

        assert (self.legal_check())

        self.filepath = filepath

        # !!! pinYin_count is essential,
        # users can use existing pinYin_count to warn startup,
        # default is using empty pinYin_count as cold startup.
        self.pinYin_count = pinYin_count

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
        assert (step % 2 == 0)

        # Read one pair of bytes
        if step == 2:
            self.pos += step
            return struct.unpack(self.format,
                                 self.rawdata[self.pos - 2:self.pos])[0]

        # Read several pair of bytes
        grouped_each_pairBytes = [
            self.rawdata[self.pos + i * 2:self.pos + i * 2 + 2]
            for i in range(step >> 1)
        ]
        self.pos += step
        return [
            struct.unpack(self.format, e)[0] for e in grouped_each_pairBytes
        ]

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
        self.Name = self._str(self._forward(0x330 - self.pos))
        self.Type = self._str(self._forward(0x540 - self.pos))
        self.Description = self._str(self._forward(0xd40 - self.pos))
        self.Example = self._str(self._forward(self.pinYin_offset - self.pos))

    def read_pinYin_table(self):
        # Read pinYin table of the .scel file
        # Starts with self.pinYin_offset
        self.pos = self.pinYin_offset

        # Will generate pinYin table and count,
        # table: table of pinYins,
        # count: count of pinYins
        self.pinYin_table = dict()

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
            self.pinYin_count[pinYin] = [0, dict()]

        return self.pinYin_table

    def get_pinYin(self, idx):
        # Check out the [idx] of the pinYin table
        return self.pinYin_table.get(idx, '--')

    def read_ciZu(self):
        # Read ciZu in the .scel file
        # Starts with self.ciZu_offset
        self.pos = self.ciZu_offset

        # Will generate words list,
        # each word is three elements tuple: (count, pinYin, ciZu)
        self.words = []

        # Read until reach the end of the file
        # Structure is (num x 2, length x 2, pinYin_idxs x length, wordarea x num),
        # structure of wordarea is (length x 2, word x length, length x 2, extend x length) repeat num times,
        # structure of extend is (count x 2, ???)
        while self.pos < len(self.rawdata):
            # count of ciZu with the same pinYin
            num = self._forward()
            # length of pinYin bytes
            length = self._forward()
            # pinYin
            pinYin_idxs = self._forward(length)
            pinYin = '\''.join([self.get_pinYin(idx) for idx in pinYin_idxs])

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

                # Add pinYin into pinYin_count
                _pinYin = pinYin.replace('\'', '')
                if _pinYin not in self.pinYin_count:
                    self.pinYin_count[_pinYin] = [0, dict()]
                self.pinYin_count[_pinYin][0] += count
                self.pinYin_count[_pinYin][1][word] = count

                # Split single char,
                # !!! char here means chinese character not pinYin letter,
                # and add single char pinYin into pinYin_count
                for py, char in zip(pinYin.split('\''), word):
                    self.pinYin_count[py][0] += count
                    # Frequency count of single char,
                    # it will be very large,
                    # compare to pinYin of a ciZu
                    if char not in self.pinYin_count[py][1]:
                        self.pinYin_count[py][1][char] = 0
                    self.pinYin_count[py][1][char] += count

        return self.words


# %%
# File settings
if True:
    folder = os.path.join(os.path.dirname(__file__), '..', 'cellDicts')

    for name in os.listdir(folder):
        if not name.endswith('.scel'):
            continue
        print(name)
        celldict = SCEL_cellDict(os.path.join(folder, name))
        celldict.pipeline()
        celldict.solid_pinYin_count()

# %%

folder = os.path.join(os.path.dirname(__file__), '..', 'cellDicts')
frames = [pd.read_json(os.path.join(folder, name))
          for name in os.listdir(folder)
          if all([name.startswith('_'),
                  name.endswith('json')])]

frames

# %%
merged_frame = pd.concat(frames, axis=1)
merged_frame.Candidates = merged_frame.Candidates.fillna({})
merged_frame.Count = merged_frame.Count.fillna(0)
merged_frame['Count'] = [e for e in merged_frame.pop('Count').values]
merged_frame['Candidates'] = [e for e in merged_frame.pop('Candidates').values]

merged_frame.Count = merged_frame.Count.map(lambda x: int(sum(x)))


def merge_dicts(dicts):
    merged = dict()
    for dct in dicts:
        if not isinstance(dct, dict):
            continue
        for key, value in dct.items():
            if key in merged:
                merged[key] += value
            else:
                merged[key] = value
    return merged


merged_frame.Candidates = merged_frame.Candidates.map(merge_dicts)
merged_frame.to_json(os.path.join(folder, 'merged.json'))
merged_frame

# %%
