# Local toolbox

import jieba
import pandas as pd


def split_words(sentence):
    split = [e.strip() for e in jieba.cut(sentence)]
    return pd.Series(split)
