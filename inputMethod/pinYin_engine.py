# File: pinYin_engine.py
# Package: inputMethod
# Aim: Provide functional engine of pinYin inputMethod interface

# %%
import os
import pandas as pd


class PinYinEngine(object):
    def __init__(self, frame_path):
        # Init the engine with dataframe in [frame_path]
        self.frame = pd.read_json(frame_path)

    def has_pinYin(self, pinYin):
        # Tell if the frame has [pinYin] index
        if len(pinYin) == 0:
            return True
        return pinYin in self.frame.index

    def split(self, content):
        # Split [content] using longest match method
        # [content] should be string
        assert (isinstance(content, str))

        # If got empty string,
        # return empty string directly
        if len(content) == 0:
            return ''

        # Using floating window to split
        segments = []
        while len(content) > 0:
            # for _ in range(10):
            # Find longest matched pattern from tail to head,
            # add the matched pattern into [segments],
            # if pattern is found in frame,
            # or the remaining pattern has only one character,
            # !!! Make sure the content is eventually cut to nothing.
            for j in range(len(content)):
                e = len(content) - j
                if self.has_pinYin(content[:e]) or e == 1:
                    segments.append(content[:e])
                    content = content[e:]
                    break
        return segments


# %%
frame_path = os.path.join(os.path.dirname(__file__), '..', 'cellDicts',
                          '_计算机词汇大全【官方推荐】.scel.json')

engine = PinYinEngine(frame_path)
engine.frame

# %%
engine.split('aozuoyi')

# %%