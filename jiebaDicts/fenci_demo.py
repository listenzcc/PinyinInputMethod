# File: fenci_demo.py
# Aim: Demo of jieba fenci

# %%
import pypinyin
import jieba
from pypinyin import pinyin, lazy_pinyin, Style

# %%
txt = open('material.txt', 'rb').read().decode('utf-8')
txt
# %%

cut = jieba.cut(txt, cut_all=True)
split = [e.strip() for e in cut]
split = [e for e in split if e]

' | '.join(split)
# %%


def is_pinYin(s):
    # Return if the [s] is a valid pinYin
    return all([
        s[0] >= 'a',
        s[0] <= 'z'
    ])


for j, ciZu in enumerate(split):
    pinYin = ''.join(lazy_pinyin(ciZu))
    if not is_pinYin(pinYin):
        pinYin = '--'
    print(j, ciZu, pinYin)
# %%
