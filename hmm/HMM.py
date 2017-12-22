#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2017/12/22 14:31
# @Author  : BigDin
# @Contact : dinglei_1107@outlook.com


class FirstOrderHMM:
    """
    (A) 一阶隐马模型基于两种简化的假设：
    1. 特定状态出现概率只依赖于它的上一期状态；
    2. 观测值的输出概率只依赖于它当期的状态；
    
    (B) 构成隐马模型的几个组件（不同版本有一些不同）：
    1. 状态转移概率矩阵：tran_prob_mat
    2. 映射概率矩阵：emi_prob_mat
    3. 状态序列：states_set
    4. 观测值序列：obs_arr
    5. 开始状态：start_state
    6. 结束状态：end_state
    
    (C) 三个基础问题
    1. Likelihood：已知模型和观测值序列，计算该序列出现的概率；
    2. Decoding：已知模型和观测值序列，计算最有可能的隐状态序列；
    3. Learning：已知观测值序列和隐状态集合，计算隐马模型；
    """
    def __init__(self,
                 tran_prob_mat,
                 emi_prob_mat,
                 states_set,
                 obs_arr,
                 start_state,
                 end_state):
        self.tran_prob_mat = tran_prob_mat
        self.emi_prob_mat = emi_prob_mat
        self.states_set = states_set
        self.obs_arr = obs_arr
        self.start_state = start_state
        self.end_state = end_state



