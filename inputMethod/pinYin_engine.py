# File: pinYin_engine.py
# Package: inputMethod
# Aim: Provide functional engine of pinYin inputMethod interface

# %%
import json
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


def merge_dicts(dicts):
    if isinstance(dicts, dict):
        dicts = [dicts]

    merged = dict()
    for dct in dicts:
        if not isinstance(dct, dict):
            continue
        for key, value in dct.items():
            if key in merged:
                merged[key] += value
            else:
                merged[key] = value

    return sorted(merged.items(), key=lambda x: x[1], reverse=True)


class PinYinTree(object):
    # PinYin tree for quickly checkout
    def __init__(self):
        self.root = dict()
        logger.debug('Tree initalized')

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
        # the remains and the found will be recorded synchronously.
        founds = dict()
        node = self.root
        pos = 0
        while pos < len(track):
            if '=' in node:
                # Find known pinYin
                founds[track[:pos]] = track[pos:]
                for guessed in self.walk_to_ends(node):
                    founds[guessed] = track[pos:]

            if track[pos] not in node:
                # Can not move forward
                founds[track[:pos]] = track[pos:]
                for guessed in self.walk_to_ends(node):
                    founds[guessed] = track[pos:]
                return founds

            if track[pos] in node:
                # Can move forward
                node = node[track[pos]]
                pos += 1
                continue

        founds[track] = ''
        for guessed in self.walk_to_ends(node):
            founds[guessed] = ''
        return founds

    def walk_to_ends(self, node, limit=3):
        # Walk from [node] to every available ends,
        # [limit] is the maximum allowed ends
        self.this_ends = []
        self.this_ends_limit = limit
        for nxt in [e for e in node if not e == '=']:
            self._walk_to_ends(node[nxt])
            if not len(self.this_ends) < self.this_ends_limit:
                break
        return self.this_ends

    def _walk_to_ends(self, node):
        if '=' in node:
            self.this_ends.append(node['='])
            if not len(self.this_ends) < self.this_ends_limit:
                return
        for nxt in [e for e in node if not e == '=']:
            if not len(self.this_ends) < self.this_ends_limit:
                break
            self._walk_to_ends(node[nxt])


class PinYinEngine(object):
    # Main engine of parsing pinYin
    def __init__(self, frame_path):
        # Init the engine with dataframe in [frame_path]
        # Read frame from [frame_path]
        self.frame = pd.read_json(frame_path)
        self.tree = PinYinTree()
        self.tree.generate(self.frame)

        self.go = True

    def has_pinYin(self, pinYin):
        # Tell if the frame has [pinYin] index
        if len(pinYin) == 0:
            return False
        return pinYin in self.frame.index

    def fetch(self, pinYin):
        # Fetch ciZu of [pinYin] in the frame
        try:
            cands = self.frame.Candidates.loc[pinYin]
        except NameError:
            logger.error(f'Can not fetch {pinYin} from the frame')
            return []
        return [e for e in cands.items()]

    def checkout(self, inp, return_json=False):
        # Checkout [inp] from the frame,
        # the results will be returned as [fetched] in DataFrame type,
        # the output [fetched] will be converted into json type if [return_json] is set to True

        # Record start time
        t = time.time()

        # Parse [inp] using pinYin Tree
        parsed = self.tree.walk_through(inp)
        fetched = pd.DataFrame()
        for key in sorted(parsed, reverse=True):
            remain = parsed[key]
            name = f'{key}\'{remain}'

            # Find records based on [key]
            if key not in self.frame.index:
                # No [key] record found
                continue
            found = self.frame.loc[key]
            found.name = name
            fetched = fetched.append(found)

        if len(fetched) == 0:
            # No records found
            return '{}'

        fetched.Candidates = fetched.Candidates.map(merge_dicts)
        fetched['Num'] = fetched.Candidates.map(len)
        fetched = fetched[['Candidates', 'Num']]
        if return_json:
            fetched = fetched.to_json()

        logger.debug(f'Checkout {inp} used {time.time() - t} seconds')
        return fetched

    def to_pandas(self, fetched):
        # Convert [fetched] to pandas DataFrame,
        # [fetched] is from the checkout method

        cat = []
        for pinYin in fetched:
            cat.extend([[pinYin, e[0], e[1]] for e in fetched[pinYin]])

        frame = pd.DataFrame(cat, columns=['PinYin', 'CiZu', 'Count'])
        return frame


# %%
if __name__ == '__main__':
    folder = os.path.join(os.path.dirname(__file__), '..', 'cellDicts')
    engine = PinYinEngine(os.path.join(folder, 'merged.json'))
    engine.frame

    fetched = engine.checkout('dian', return_json=False)
    display(fetched)

# %%
# b = engine.checkout('dian')
# b

# %%
