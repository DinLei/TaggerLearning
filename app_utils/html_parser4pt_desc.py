#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2017/10/20 11:31
# @Author  : BigDin
# @Contact : dinglei_1107@outlook.com

"""
需要安装的包：
    1) lxml: 解析html
    2) csv:  读取csv
"""
import re
from lxml import etree
# 抽取商品描述信息

stop_words = {"a", "an", "the", "this", "that", "there", "those"}


def get_pt_describe(root_html):
    context = []
    try:
        parse = etree.HTML(root_html)
        body = parse.find("body")
        rm_node(body, node_name="table")
        br_p_span(context, body)
    except Exception as e:
        print(e)
    finally:
        return context


def get_wap_describe(root_html):
    parse = etree.HTML(root_html)
    context = []
    try:
        target = parse.xpath("//tr")
        for tr in target:
            tmp = []
            print(tr)
            tds = tr.xpath("./td")
            for td in tds:
                tmp_str = td.text.strip()
                print(tmp_str)
                sub_tmp = []
                br_p_span(sub_tmp, td, "./br|./span|.//strong")
                tmp_str += ", ".join(sub_tmp)
                if tmp_str:
                    tmp_str = re.sub(r"//", "", tmp_str)
                    tmp_str = re.sub("\xa0", " ", tmp_str)
                    tmp_str = re.sub("\s{2,}", " ", tmp_str)
                    tmp.append(tmp_str.lower().strip())
            if tmp:
                context.append(": ".join(tmp))
    except Exception as e:
        print(e)
    finally:
        return context


def br_p_span(context, parse, xpath_rule="//br | //p | //span"):
    target = parse.xpath(xpath_rule)
    for t in target:
        if t.tail:
            info = t.tail
        elif t.text:
            info = t.text
        else:
            continue
        if info.strip():
            info = re.sub("-", "", info)
            info = re.sub("'", "", info)
            info = re.sub("\"", "", info)
            info = re.sub("//", "", info)
            info = re.sub("\xa0", " ", info)
            words_info = [x for x in info.split() if x not in stop_words]
            info = " ".join(words_info)
            info = re.sub("\s{2,}", " ", info)
            context.append(info.lower().strip())


def rm_node(parse, node_name="table"):
    tmp = parse.findall(node_name)
    if tmp:
        for tn in tmp:
            parse.remove(tn)
    divs = parse.findall("div")
    if divs:
        for div in divs:
            rm_node(div, node_name)


if __name__ == "__main__":
    pass

