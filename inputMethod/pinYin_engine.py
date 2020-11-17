# File: pinYin_engine.py
# Package: inputMethod
# Aim: Provide functional engine of pinYin inputMethod interface

# %%
import logging
import os
import sys
import pandas as pd
import time

logger = logging.getLogger('Engine')
handler = logging.StreamHandler(sys.stdout)
if len(logger.handlers) == 0:
    logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class PinYinTree(object):
    # PinYin tree for quickly checkout
    def __init__(self):
        self.root = dict()

    def generate(self, frame):
        # Generate based on [frame]
        # Count the elapsed time,
        # since it may slow
        t = time.time()
        for pinYin in frame.index:
            self.add(pinYin)
        logger.debug('Tree generation used {} seconds'.format(time.time() - t))

    def add(self, pinYin):
        # Add new [pinYin] to the tree
        # Adding is from the root
        node = self.root
        # Add characters one-by-one, step-by-step
        for c in pinYin:
            if c not in node:
                # Add new key as [c] to the node
                node[c] = dict()
            # Move forward
            node = node[c]
        # Reach the end of the pinYin
        node['='] = pinYin

    def walk_through(self, track):
        # Walk through the tree using the [track],
        # record the known pinYins during the travel,
        # the remains and the found will be recorded synatisticlly.
        founds = []
        node = self.root
        remain = track
        while len(remain) > 0:
            if '=' in node:
                # Find known pinYin
                founds.append([node['='], remain])

            if remain[0] not in node:
                # Can not move forward
                founds.append(['-', remain])
                node = self.root
                print('- Back to root')
                continue

            if remain[0] in node:
                # Can move forward
                node = node[remain[0]]
                print(f'- Forward to {remain[0]}')
                remain = remain[1:]
                continue

        if '=' in node:
            # Find known pinYin in the last character
            founds.append([node['='], remain])
        else:
            # Unknow the pinYin in the last character
            founds.append(['-', remain])

        return founds

    def checkout(self, track):
        # Checkout all known pinYins using [track]
        # [track] may be incomplete pinYin segment
        t = time.time()

        # Checkout from the root
        node = self.root
        for j, step in enumerate(track):
            if not step in node:
                # Found non-matching step,
                # something is wrong,
                # logging error and return with None
                logger.error(f'Fail to checkout: {track} on {j}_th char')
                return None

            # Move forward
            node = node[step]

        # See what we got
        logger.debug(f'Checkout "{track}" used {time.time() - t} seconds')
        return node


class PinYinEngine(object):
    # Main engine of parsing pinYin
    def __init__(self, frame_path):
        # Init the engine with dataframe in [frame_path]
        self.frame = pd.read_json(frame_path)

    def has_pinYin(self, pinYin):
        # Tell if the frame has [pinYin] index
        if len(pinYin) == 0:
            return True
        return pinYin in self.frame.index

    def checkout(self, key):
        # Checkout pinYins startswith [key]
        t = time.time()
        found = self.frame.loc[self.frame.index.map(
            lambda x: x.startswith(key))]
        logger.debug(
            f'Checkout startswith "{key}" used {time.time() - t} seconds')
        return found

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
tree = PinYinTree()
tree.generate(engine.frame)
# tree.root

# %%
tree.walk_through('zuoyezhouqi')

# %%
tree.walk_through('zuoyzhouqi')
# %%
# engine.checkout('zuo')

# %%
# tree.checkout('an')
# %%
# engine.frame.loc[['a', 'an']]
# %%
# engine.frame.loc[engine.frame.index.map(lambda x: x.startswith('a'))]
# %%
