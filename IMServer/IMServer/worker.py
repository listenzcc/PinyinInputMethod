# Backend worker
import os
import pandas as pd
import jieba
import re

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


def match(pattern, string):
    return re.match(pattern, string) is not None


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

    def mk_contentframe(self, contents):
        cf = pd.DataFrame(contents)
        cf.columns = ['sentence']
        self.cf = cf

    def query(self, pinYin):
        # found = self.df[self.df['pinYin'].str.startswith(pinYin)]
        p = '.*'.join(pinYin)
        p = p + '.*'
        found = self.df[self.df['pinYin'].map(lambda e: match(p, e))]
        return found

    def guess(self, zi):
        def cut(s, zi=zi):
            j = max(s.find(zi)-4, 0)
            c = s[j:]
            return c.replace(zi, f'<strong>{zi}</strong>')

        found = self.cf[self.cf['sentence'].str.contains(zi)]
        found['sentence'] = found['sentence'].map(cut)
        return found


data = Data()

for string in tqdm(contents):
    ciZu = sorted(set([e.strip() for e in jieba.cut(string, cut_all=True)]))
    for c in ciZu:
        pinYin = ''.join(lazy_pinyin(c))
        data.add(pinYin, c)

data.mk_dataframe()
data.mk_contentframe(contents)
