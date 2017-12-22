#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2017/11/6 15:00
# @Author  : BigDin
# @Contact : dinglei_1107@outlook.com

import nltk
from fuzzywuzzy import process


class FuzzyMatch:
    """
    模糊匹配，寻找关键字
    """
    @staticmethod
    def top_fuzzy(base_keywords, source, limit=3):
        assert isinstance(source, list) or isinstance(source, set)
        assert isinstance(base_keywords, str) or isinstance(base_keywords, list) or isinstance(base_keywords, set)
        limit = min(limit, len(source))
        if isinstance(base_keywords, str):
            fuzzy_phrase = [x[0] for x in process.extract(base_keywords, source, limit=limit)]
            tmp = []
            for phrase in fuzzy_phrase:
                tmp.extend(nltk.word_tokenize(phrase))
            fuzzy_words = process.extract(base_keywords, tmp, limit=limit)
            return [x[0] for x in fuzzy_words]
        else:
            outcome = dict()
            for keyword in base_keywords:
                outcome[keyword] = FuzzyMatch.top_fuzzy(base_keywords=keyword, source=source, limit=limit)
            return outcome


if __name__ == "__main__":
    season_field = ["spring", "summer", "autumn", "winter"]
    # season_field = "winter"
    finds = {'after school', 'big: wonter',
             "season: winter; today is sunday",
             "summer is funny"}
    print(FuzzyMatch.top_fuzzy(season_field, finds))
