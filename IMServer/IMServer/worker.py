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


def match(r, string):
    '''
    Whether the [string] matches with [r]

    Args:
    - @r: The pre compiled regular expression
    - @string: The string to be tested

    Out:
    - True if match, False if not
    '''
    return r.match(string) is not None


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
        r = re.compile(p)
        found = self.pinYin_table[self.pinYin_table['pinYin'].map(
            lambda e: match(r, e))]

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


worker = Worker()
