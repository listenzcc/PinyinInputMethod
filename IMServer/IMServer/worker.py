# Backend worker

# Imports
import os
import pandas as pd
import jieba
import re

from tqdm.auto import tqdm
from pypinyin import pinyin, lazy_pinyin, Style

# Settings
# The folder of materials
folder = os.path.join(os.path.dirname(__file__), '..', '..', 'txt')
# The segments of sentences
segments = ['\r', '\n', '。', '；']

# Read contents from .txt file in [folder]
contents = []
for fname in os.listdir(folder):
    contents.append(open(os.path.join(folder, fname),
                         'rb').read().decode(errors='ignore'))

contents = '\n'.join(contents)
for s in segments:
    contents = contents.replace(s, '\n')

contents = [e.strip() for e in contents.split('\n') if e.strip()]
contents = sorted(set(contents))
contents


# Local functions
def match(pattern, string):
    '''
    Whether the [string] matches with [pattern]

    Args:
    - @pattern: The pattern of re
    - @string: The string to be tested

    Out:
    - Boolean variable of the matching
    '''
    return re.match(pattern, string) is not None


class Data(object):
    '''
    Data object of pinYin input method.
    '''

    def __init__(self):
        '''
        Build empty dataset
        The empty [self.data] as the type of dict will be generated.
        '''
        self.data = dict()

    def add(self, pinYin, ciZu):
        '''
        Add [pinYin] and [ciZu] into the dataset
        - @pinYin: The pinYin string, in characters
        - @ciZu: The ciZu string, in chinese-words

        The [self.data] will be updated,
        - key: The pinYin string
        - value: [{ciZu}, freq]
        - {ciZu}: The set of several ciZu to the key 
        - freq: The frequency of occuring of the pinYin
        '''
        if pinYin not in self.data:
            self.data[pinYin] = [{ciZu}, 1]
        else:
            self.data[pinYin][0].add(ciZu)
            self.data[pinYin][1] += 1

    def mk_dataframe(self):
        '''
        Make DataFrame of pinYins and their candidates ciZus,
        based on the [self.data].
        It should be operated, **AFTER** users have finished adding the pinYin and ciZu pairs.

        The [self.df] will be generated,
        the columns are ['pinYin', 'candidates', 'freq'],
        where 'candidates' refers all the ciZu
        '''
        df = pd.DataFrame()
        df['tmp'] = self.data.values()
        df['candidates'] = df['tmp'].map(lambda e: e[0])
        df['freq'] = df['tmp'].map(lambda e: e[1])
        df['pinYin'] = self.data.keys()
        df = df[['pinYin', 'candidates', 'freq']]
        self.df = df.sort_values('freq', ascending=False)

    def mk_contentframe(self, contents):
        '''
        Make DataFrame of contents,
        it contains all the sentences in the txt materials,
        it is designed for checkout ciZu from the sentences.

        The [self.cf] will be generated,
        the column is 'sentence'.
        '''
        cf = pd.DataFrame(contents)
        cf.columns = ['sentence']
        self.cf = cf

    def query(self, pinYin):
        '''
        Checkout [pinYin] for the ciZu candidates,
        the [self.df] DataFrame is used to be checked,
        the regular express is used to use the vague matching.

        Args:
        - @pinYin: The pinYin string to be matched

        Outs:
        - @found: The found rows of the [self.df]
        '''
        p = '.*'.join(pinYin)
        p = p + '.*'
        found = self.df[self.df['pinYin'].map(lambda e: match(p, e))]
        return found

    def guess(self, zi):
        '''
        Checkout [zi] out of the [self.cf],
        it finds sentence with [zi] inside them,
        the output is the series of the slices of the finds with the [zi] at **head but not the first** of it.

        Args:
        - @zi: The zi to be found 

        Outs:
        - @found: The found sentence slices
        '''
        def cut(s, zi=zi):
            j = max(s.find(zi)-4, 0)
            c = s[j:]
            return c.replace(zi, f'<strong>{zi}</strong>')

        found = self.cf[self.cf['sentence'].str.contains(zi)]
        found['sentence'] = found['sentence'].map(cut)
        return found


# Init data object
data = Data()

# Feed the data using contents,
# for each sentence, cut it into ciZus using jieba,
# and generate the pinYin for each ciZu,
# update the data using the pinYin and ciZu
for string in tqdm(contents):
    ciZu = sorted(set([e.strip() for e in jieba.cut(string, cut_all=True)]))
    for c in ciZu:
        pinYin = ''.join(lazy_pinyin(c))
        data.add(pinYin, c)

# Make up data
# Make df
data.mk_dataframe()
# Make cf
data.mk_contentframe(contents)
