# Backend worker

# ! This one is ready to be replaced by a simpler worker,
# ! in which, it has only the query method,
# ! since the data has been made by in another dataset.

# Imports
import os
import re
import json
import pandas as pd

from . import cfg


def match(pattern, string):
    '''
    Whether the [string] matches with [pattern]

    Args:
    - @pattern: The pattern of re
    - @string: The string to be tested

    Out:
    - True if match, False if not
    '''
    return re.match(pattern, string) is not None


def regular(df, columns):
    '''Regular the [df],
    the [columns] will be selected,
    the index will be restored as 1, 2, ...

    Args:
    - @df: The DataFrame to be regularized;
    - @columns: The columns to be filtered.

    Outs:
    - The regularized DataFrame.
    '''
    df.index = range(len(df))
    return df[columns]


class Worker(object):
    '''The backend worker of the input method.
    '''

    def __init__(self, cfg=cfg):
        '''The initialization of the worker.

        The pinYin_table and ciZu_table will be loaded.
        The path of them are provided in prior.

        Args:
        - @ cfg: The config object, default value is cfg in prior.
        '''
        self.pinYin_table = pd.read_json(cfg.get('pinYinTable', 'Path'))
        self.ciZu_table = pd.read_json(cfg.get('ciZuTable', 'Path'))
        return

    def query(self, pinYin):
        '''Query the ciZu of the[pinYin],
        the vague matching method is used,
        for example, "abc" matches with the patterns like "axxbyczz".

        Args:
        - @pinYin: The pinYin string to be queried.

        Outs:
        - @ciZu_json: The found slices.
        '''

        columns = ['pinYin', 'ciZus', 'count']

        p = '.*'.join(pinYin)
        p = p + '.*'
        found = self.pinYin_table[self.pinYin_table['pinYin'].map(
            lambda e: match(p, e))]

        return regular(found, columns)

    def suggest(self, ciZu):
        '''Check out some suggestion of the[ciZu] input.

        Args:
        - @ciZu: The ciZu of being checked.

        Outs:
        - @suggest_json: The slices of suggestions.
        '''
        columns = ['ciZu', 'pinYin', 'suggests']

        found = self.ciZu_table.query(f'ciZu == "{ciZu}"')

        return regular(found, columns)


class OldWorker(object):
    '''
    ! To be deleted
    '''

    def query(self, pinYin):
        '''
        Checkout[pinYin] for the ciZu candidates,
        the[self.df] DataFrame is used to be checked,
        the regular express is used to use the vague matching.

        Args:
        - @ pinYin: The pinYin string to be matched

        Outs:
        - @ found: The found rows of the[self.df]
        '''
        p = '.*'.join(pinYin)
        p = p + '.*'
        found = self.df[self.df['pinYin'].map(lambda e: match(p, e))]
        return found

    def guess(self, zi):
        '''
        Checkout[zi] out of the[self.cf],
        it finds sentence with [zi] inside them,
        the output is the series of the slices of the finds with the[zi] at ** head but not the first ** of it.

        Args:
        - @ zi: The zi to be found

        Outs:
        - @ found: The found sentence slices
        '''
        def cut(s, zi=zi):
            j = max(s.find(zi)-4, 0)
            c = s[j:]
            return c.replace(zi, f'<strong>{zi}</strong>')

        found = self.cf[self.cf['sentence'].str.contains(zi)]
        found['sentence'] = found['sentence'].map(cut)
        return found

    def save_data(self, path_prefix=data_prefix):
        '''
        Save[self.df] and [self.cf] as [path_prefix],
        make sure the DataFrames have been generated in advance,
        use[self.mk_dataframe] and [self.mk_contentframe] to generate the DataFrames
        - @ path_prefix: The prefix of saved data files, in full path mode
        '''
        self.cf.to_json(path_prefix + '-cf.json')
        self.df.to_json(path_prefix + '-df.json')

    def load_data(self, path_prefix=data_prefix):
        '''
        Load[self.df] and [self.cf] as [path_prefix],
        make sure the files exist in advance,
        the operation will overwrite the existing DataFrames
        - @ path_prefix: The prefix of saved data files, in full path mode
        '''
        self.cf = pd.read_json(path_prefix + '-cf.json')
        self.df = pd.read_json(path_prefix + '-df.json')


# Init data object
data = Data()

if new_session:
    # Make up data
    # Feed the data using contents,
    # for each sentence, cut it into ciZus using jieba,
    # and generate the pinYin for each ciZu,
    # update the data using the pinYin and ciZu
    for string in tqdm(contents):
        ciZu = sorted(set([e.strip()
                           for e in jieba.cut(string, cut_all=True)]))
        for c in ciZu:
            pinYin = ''.join(lazy_pinyin(c))
            data.add(pinYin, c)

    # Make df
    data.mk_dataframe()

    # Make cf
    data.mk_contentframe(contents)

    # Save latest DataFrames
    data.save_data()

else:
    data.load_data()
