# Local toolbox

import jieba
import pandas as pd


def split_words(sentence):
    '''Split the [sentence] using jieba.

    Args:
    - @sentence: The sentence to split.

    Outs:
    - The Series of splitted words.
    '''
    split = [e.strip() for e in jieba.cut(sentence)]
    return pd.Series(split)
