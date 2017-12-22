#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2017/12/18 17:41
# @Author  : BigDin
# @Contact : dinglei_1107@outlook.com

import pandas as pd
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag, word_tokenize

LEMMA = WordNetLemmatizer()


# 离散数据one-hot-encode处理
def one_hot_encoder(data, discrete_cols=None, del_cols=None):
    """
    对离散变量进行one-hot编码
    :param data: pd.DataFrame
    :param discrete_cols: 
    :param del_cols: 
    :return: 变换后的data，pd.DataFrame
    """
    if not discrete_cols:
        discrete_cols = set(data.columns)
    else:
        discrete_cols = set(discrete_cols)
    if del_cols:
        for col in del_cols:
            discrete_cols.remove(col)
    assert isinstance(data, pd.core.frame.DataFrame)
    new_data = None
    for column in discrete_cols:
        print("\tDiscretize the feature:【{}】...".format(column))
        tmp = pd.get_dummies(data[column], prefix=column)
        new_data = pd.concat([new_data, tmp], axis=1)
    print("Features discretization task completed!")
    return new_data


def text_vector_model(text_data, weighted='tf', binary=True,
                      ngram_range=(1, 3), max_df=0.99,
                      min_df=1, max_features=None):
    from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
    assert weighted in {'tf', 'tf-idf'}
    if weighted == 'tf_idf':
        model = TfidfVectorizer(ngram_range=ngram_range, max_df=max_df,
                                min_df=min_df, binary=binary, max_features=max_features)
    else:
        model = CountVectorizer(ngram_range=ngram_range, max_df=max_df,
                                min_df=min_df, binary=binary, max_features=max_features)
    return model.fit(text_data)


def text2vec(texts, t2v_model):
    return t2v_model.transform(texts)


def lemma_sentence(sentence):
    res = []
    for word, pos in pos_tag(word_tokenize(sentence)):
        word_net_pos = get_word_net_pos(pos) or wordnet.NOUN
        res.append(LEMMA.lemmatize(word, pos=word_net_pos))
    return " ".join(res)


def get_word_net_pos(word_tag):
    if word_tag.startswith('J'):
        return wordnet.ADJ
    elif word_tag.startswith('V'):
        return wordnet.VERB
    elif word_tag.startswith('N'):
        return wordnet.NOUN
    elif word_tag.startswith('R'):
        return wordnet.ADV
    else:
        return None
