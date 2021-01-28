# Backend worker
import os
import pandas as pd
import jieba

from tqdm.auto import tqdm
from pypinyin import pinyin, lazy_pinyin, Style

folder = os.path.join(os.path.dirname(__file__), '..', '..', 'txt')
segments = ['\r', '\n', '。', '；']

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


class Data(object):
    def __init__(self):
        self.data = dict()

    def add(self, pinYin, ciZu):
        if pinYin not in self.data:
            self.data[pinYin] = [{ciZu}, 1]
        else:
            self.data[pinYin][0].add(ciZu)
            self.data[pinYin][1] += 1

    def mk_dataframe(self):
        df = pd.DataFrame()
        df['tmp'] = self.data.values()
        df['candidates'] = df['tmp'].map(lambda e: e[0])
        df['freq'] = df['tmp'].map(lambda e: e[1])
        df['pinYin'] = self.data.keys()
        df = df[['pinYin', 'candidates', 'freq']]
        self.df = df.sort_values('freq', ascending=False)
        return df

    def query(self, pinYin):
        return self.df[self.df['pinYin'].str.startswith(pinYin)]


data = Data()

for string in tqdm(contents):
    ciZu = sorted(set([e.strip() for e in jieba.cut(string, cut_all=True)]))
    for c in ciZu:
        pinYin = ''.join(lazy_pinyin(c))
        data.add(pinYin, c)

data.mk_dataframe()
