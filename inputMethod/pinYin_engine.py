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

    def found_match_pattern(self, pattern, remain, node):
        # Found matched pattern,
        # the original query is string of [pattern] + [remain],
        # [node] is current node, derived from root using [pattern].
        pass

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

            if track[pos] not in node:
                # Can not move forward
                founds[track[:pos]] = track[pos:]
                return founds

            if track[pos] in node:
                # Can move forward
                node = node[track[pos]]
                pos += 1
                continue

        founds[track] = ''
        return founds


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
        self.go = True
        t = time.time()

        # Parse [inp] using pinYin Tree
        parsed = self.tree.walk_through(inp)
        fetched = pd.DataFrame()
        for key in sorted(parsed, reverse=True):
            remain = parsed[key]
            name = f'{key}\'{remain}'
            if len(remain) == 0:
                found = self.frame.loc[self.frame.index.map(
                    lambda x: x.startswith(key))]
            else:
                found = self.frame.loc[self.frame.index.map(lambda x: all(
                    [x.startswith(key), not x.startswith(key + remain[0])]))]

            fetched = fetched.append(
                pd.Series(dict(Candidates=found.Candidates.to_list()),
                          name=name))

            if not self.go:
                logger.debug(
                    f'---- Checkout {inp} used {time.time() - t} seconds')
                return '{}'

        fetched.Candidates = fetched.Candidates.map(merge_dicts)
        fetched['Num'] = fetched.Candidates.map(len)
        if return_json:
            fetched = fetched.to_json()

        logger.debug(f'Checkout {inp} used {time.time() - t} seconds')
        return fetched
        # print(parsed)

        # Fetch contents from the frame,
        # [fetched] is a dict:
        #   key is pinYin of longest matched;
        #   value is the list of ciZu and its frequency count.
        fetched = dict()
        for pinYin, remain, guessed in parsed:
            # Fetch [pinYin] or [guessed] pinYin from the frame,
            # the fetched ciZus will be sorted by their frequency count
            _pinYin = f'{pinYin}\'{remain}'

            if len(guessed) == 0 and not pinYin.endswith('...'):
                # The pinYin is of complete match
                fetched[_pinYin] = sorted(self.fetch(pinYin),
                                          reverse=True,
                                          key=lambda x: x[1])

            else:
                # The pinYin is of partial match,
                # fetch every possible auto-completed match [guessed]
                all_guess = []
                best_guess = []
                for py in guessed:
                    all_guess += self.fetch(py)

                    # Give some "intelligence" to the fetcher,
                    # if the guessed pinYin ends with "remain",
                    # the pinYin will be stored in [best_guess]
                    if py.endswith(remain) and len(py) > len(inp):
                        best_guess += self.fetch(py)

                fetched[pinYin + remain] = sorted(best_guess,
                                                  reverse=True,
                                                  key=lambda x: x[1])

                if len(remain) > 0:
                    # If remain is empty string,
                    # avoid add the guessed pinYins since they are the same as [best_guess]
                    fetched[_pinYin] = sorted(all_guess,
                                              reverse=True,
                                              key=lambda x: x[1])

        # print(fetched)
        fetched = self.to_pandas(fetched)

        if return_json:
            fetched = fetched.to_json()

        logger.debug(f'Checkout "{inp}" used {time.time() - t} seconds')
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

    t = time.time()
    fetched = engine.checkout('dian', return_json=False)
    print('---', time.time() - t)
    display(fetched)

# %%
# b = engine.checkout('dian')
# b

# %%