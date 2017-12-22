#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2017/12/11 12:57
# @Author  : BigDin
# @Contact : dinglei_1107@outlook.com

import re
import os
from nltk import pos_tag
from app_utils.log_utils import get_logger
from nltk.parse.stanford import StanfordDependencyParser
from config_info.log_config import keyword_extract_logfile_name
from config_info.model_config import JAR_PATH, MODEL_PATH, COLORS

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

logger = get_logger("keyword_extract",
                    filename=os.path.join(BASE_DIR, keyword_extract_logfile_name))

# bak: regular --
# h : 25cm w : 24cm d : 12.5cm
SPECIAL_RULE = re.compile("[a-z]{1,20}\s?:\s?\d{1,5}\.?\d{0,5}[a-z]{1,5}")
COLON_RULE = re.compile(":")

ENG_PARSER = StanfordDependencyParser(
    path_to_jar=JAR_PATH + "stanford-parser.jar",
    path_to_models_jar=JAR_PATH + "stanford-parser-3.8.0-models.jar",
    model_path=MODEL_PATH + "lexparser/englishPCFG.ser.gz"
)


class KeywordParser:
    def __init__(self):
        logger.info(self.__repr__())

    @staticmethod
    def keyword_extract(text):
        text = str(text).lower()
        words = text.split()
        if len(words) == 1:
            return text
        if len(words) == 2:
            words_tag = pos_tag(words)
            if words_tag[-1][1].startswith("NN"):
                return words[-1]
        res = list(ENG_PARSER.parse(words))[0]
        candidate_root = res.root['word']
        candidate_root_tag = res.root['tag']
        candidate_nn, candidate_case, candidate_nmod = None, None, None
        words_count = {}
        for row in res.triples():
            if row[0][1].startswith("NN"):
                candidate_nn = row[0][0]
            if row[1] == "case":
                candidate_case = row[0][0]
                candidate_case_tag = row[0][1]
            if row[1] == "nmod":
                candidate_nmod = row[0][0]
                candidate_nmod_tag = row[0][1]
            if row[0][0] not in words_count:
                words_count[row[0][0]] = 0
            words_count[row[0][0]] += 1
        if len(words) > 4:
            tmp_words = sorted(words_count.items(), key=lambda x: x[1], reverse=True)
            max_nums = tmp_words[0][1]
            candidates = [ele[0] for ele in tmp_words if ele[1] == max_nums]
        else:
            candidates = words
        if candidate_nmod and candidate_nmod_tag.startswith("NN") and candidate_nmod in candidates:
            return candidate_nmod
        elif candidate_case and candidate_case_tag.startswith("NN") and candidate_case in candidates:
            return candidate_case
        elif candidate_root_tag.startswith("NN") and candidate_root in candidates:
            return candidate_root
        elif candidate_nn in candidates:
            return candidate_nn
        else:
            return candidates[0]

    def attr_value(self, text):
        """
        子属性：并列关系【,:】;说明关系【*\】
        :param text: 
        :return: 
        """
        text = str(text).lower().strip().strip(":")
        logger.info("Raw text: {}".format(text))
        if ":" not in text:
            return self._simple_attr_value(text)
        else:
            colon_nums = len(COLON_RULE.findall(text))
            if colon_nums > 2:
                with_colon_phrases = SPECIAL_RULE.findall(text)
                if len(with_colon_phrases) == colon_nums:
                    tmp_values = [x.split(":") for x in with_colon_phrases]
                    return {"unknown": [{e[0]:e[1]} for e in tmp_values]}
            attr_and_val = dict()
            split = text.index(":")
            root_attr = text[:split].strip()
            attr_and_val[root_attr] = list()

            values_arr = list()
            root_value = text[(split+1):].strip().strip(":")
            if "/" in root_value or "," in root_value:
                children = re.split(",|/|//", root_value)
                for child in children:
                    if "*" in child:
                        sub_value = self._attr_str_with_star(child)
                    elif ":" in child:
                        sub_value = self._attr_str_with_colon(child)
                    else:
                        sub_value = self._simple_attr_value(child)
                    values_arr.append(sub_value)
            elif "*" in root_value:
                sub_value = self._attr_str_with_star(root_value)
                values_arr.append(sub_value)
            elif ":" in root_value:
                sub_value = self._attr_str_with_colon(root_value)
                values_arr.append(sub_value)
            else:
                sub_value = self._simple_attr_value(root_value)
                values_arr.append(sub_value)
            values_arr = [x for x in values_arr if x]
            if len(values_arr) <= 0:
                return attr_and_val
            elif len(values_arr) == 1:
                attr_and_val[root_attr] = values_arr
                return attr_and_val
            values_arr = sorted(values_arr, key=lambda x: list(x.keys())[0])
            last_val = {}
            for val in values_arr:
                if not last_val:
                    last_val = val
                    continue
                for k, v in val.items():
                    if isinstance(v, dict):
                        if k in last_val:
                            last_val[k].update(v)
                        else:
                            attr_and_val[root_attr].append(last_val)
                            last_val = {}
                    else:
                        attr_and_val[root_attr].append(last_val)
                        last_val = val
            if last_val:
                attr_and_val[root_attr].append(last_val)
            return attr_and_val

    @staticmethod
    def color_recognize(text, keywords=None):
        words = str(text).lower().split()
        words = [w.strip() for w in words]
        colours = []
        for w in words:
            if w in COLORS:
                colours.append(w)
        if len(colours) == 1:
            return colours[0]
        elif len(colours) == 0:
            return None
        else:
            if keywords and keywords in words:
                k_id = words.index(keywords)
                min_dist = 99999999999
                candidate = None
                for cw in colours:
                    tmp_id = words.index(cw)
                    tmp_dist = abs(tmp_id-k_id)
                    if tmp_dist < min_dist:
                        min_dist = tmp_dist
                        candidate = cw
                return candidate
            else:
                return colours[-1]

    @staticmethod
    def _attr_str_with_star(text):
        try:
            text = str(text).lower().strip()
            attr_and_val = [e.strip() for e in text.split("*")]
            assert len(attr_and_val) == 2
            attr_and_val.reverse()
            return {attr_and_val[0]: attr_and_val[1]}
        except Exception as e:
            logger.debug("文本: {}, 分词后: {}.".format(text, attr_and_val))
            logger.error("[*]字段出现出现异常: %s" % e, exc_info=True)

    @staticmethod
    def _attr_str_with_colon(text):
        try:
            text = str(text).lower().strip()
            attr_and_val = [e.strip() for e in text.split(":")]
            assert 2 <= len(attr_and_val) <= 3
            if len(attr_and_val) == 2:
                return {attr_and_val[0]: attr_and_val[1]}
            else:
                return {
                    attr_and_val[0]: {
                        attr_and_val[1]: attr_and_val[2]
                    }
                }
        except Exception as e:
            logger.debug("Error ### 文本: {}, 分词后: {}.".format(text, attr_and_val))
            logger.error("[:]字段出现出现异常: %s" % e, exc_info=True)

    def _simple_attr_value(self, text):
        try:
            attr_name = self.keyword_extract(text)
            attr_value = text.replace(attr_name, "").strip()
            if attr_value == "":
                return {attr_name: attr_name}
            return {attr_name: attr_value}
        except Exception as e:
            logger.debug("Error ### 文本: {}".format(text))
            logger.error("关键词提取出现异常: %s" % e, exc_info=True)


if __name__ == "__main__":
    test = "Short sleeves"

