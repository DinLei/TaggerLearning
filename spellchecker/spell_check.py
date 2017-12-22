#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2017/11/6 14:50
# @Author  : BigDin
# @Contact : dinglei_1107@outlook.com

import enchant
from nltk.metrics import edit_distance


class SpellingReplacer(object):
    def __init__(self, dict_name='en', max_dist=2):
        self._spell_dict = None
        self._max_dist = None
        if dict_name:
            self.spell_dict = dict_name
        if max_dist:
            self.max_dist = max_dist

    def replace(self, word):
        if self.spell_dict.check(word):
            return word
        suggestions = self.spell_dict.suggest(word)
        if suggestions and edit_distance(word, suggestions[0]) <= self.max_dist:
            return suggestions[0]
        else:
            return word

    @property
    def max_dist(self):
        return self._max_dist

    @max_dist.setter
    def max_dist(self, max_dist):
        self._max_dist = max_dist

    @property
    def spell_dict(self):
        return self._spell_dict

    @spell_dict.setter
    def spell_dict(self, dict_name):
        self._spell_dict = enchant.Dict(dict_name)


if __name__ == "__main__":
    replacer = spell_check.SpellingReplacer()
    replacer.replace('insu')
