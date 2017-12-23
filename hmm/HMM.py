#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2017/12/22 14:31
# @Author  : BigDin
# @Contact : dinglei_1107@outlook.com

import numpy as np


class FirstOrderHMM:
    """
    (A) 一阶隐马模型基于两种简化的假设：
    1. 特定状态出现概率只依赖于它的上一期状态；
    2. 观测值的输出概率只依赖于它当期的状态；
    
    (B) 构成隐马模型的几个组件（不同版本有一些不同）：
    1. 状态转移概率矩阵：tran_prob
    2. 映射概率矩阵：emi_prob
    3. 状态序列：states_set
    4. 观测值集合：obs_set
    5. 开始状态：start_state
    6. 结束状态：end_state
    
    (C) 三个基础问题
    1. Likelihood：已知模型和观测值序列，计算该序列出现的概率；
    2. Decoding：已知模型和观测值序列，计算最有可能的隐状态序列；
    3. Learning：已知观测值序列和隐状态集合，计算隐马模型；
    """
    def __init__(self):
        self.tran_prob = dict()
        self.emi_prob = dict()
        self.start_prob = dict()
        self.stop_prob = dict()
        self.states = list()

    def load_hmm(self,
                 tran_prob,
                 emi_prob,
                 start_prob=None,
                 stop_prob=None):
        self.tran_prob = tran_prob
        self.emi_prob = emi_prob
        self.states = set(tran_prob.keys())
        if not start_prob:
            n_states = len(self.states)
            self.start_prob = dict(
                zip(self.states, [1/n_states]*n_states)
            )
        else:
            self.start_prob = start_prob
        if not stop_prob:
            n_states = len(self.states)
            self.stop_prob = dict(
                zip(self.states, [1/n_states]*n_states)
            )
        else:
            self.stop_prob = stop_prob

    def forward_step(self, obs):
        if not self._has_model():
            raise Exception("No hmm model!")
        forward_prob = [{}]
        for stat in self.states:
            forward_prob[0][stat] = self.start_prob[stat] * self.emi_prob[stat][obs[0]]
        for i in range(1, len(obs)):
            forward_prob.append({})
            for stat in self.states:
                forward_prob[i][stat] = sum(
                    forward_prob[i-1][prev_s] *
                    self.tran_prob[prev_s][stat] *
                    self.emi_prob[stat][obs[i]]
                    for prev_s in self.states)
        forward_prob.append({})
        for stat in self.states:
            forward_prob[-1][stat] = forward_prob[-2][stat] * self.stop_prob[stat]
        return sum(forward_prob[-1].values()), forward_prob

    def viterbi_step(self, obs):
        if not self._has_model():
            raise Exception("No hmm model!")
        optimal_seq = []
        viterbi_prob = [{}]
        for stat in self.states:
            viterbi_prob[0][stat] = {
                "prob": self.start_prob[stat] * self.emi_prob[stat][obs[0]],
                "prev": None
            }
        for i in range(1, len(obs)):
            viterbi_prob.append({})
            for stat in self.states:
                prev_max_prob = max([viterbi_prob[i-1][prev_stat]["prob"] *
                                     self.tran_prob[prev_stat][stat]
                                     for prev_stat in self.states])
                for prev_stat in self.states:
                    if viterbi_prob[i-1][prev_stat]["prob"] *\
                            self.tran_prob[prev_stat][stat] == prev_max_prob:
                        viterbi_prob[i][stat] = {
                            "prob": prev_max_prob * self.emi_prob[stat][obs[i]],
                            "prev": prev_stat
                        }
                        break
        max_prob = -1
        opt_stat = None
        for stat, info in viterbi_prob[-1].items():
            last_prob = info["prob"] * self.stop_prob[stat]
            if last_prob > max_prob:
                max_prob = last_prob
                opt_stat = stat

        optimal_seq.append(opt_stat)

        for ind in range(len(obs)-2, -1, -1):
            optimal_seq.insert(
                0,
                viterbi_prob[ind+1][opt_stat]["prev"]
            )
            opt_stat = viterbi_prob[ind+1][opt_stat]["prev"]
        return optimal_seq

    def backward_step(self, obs):
        if not self._has_model():
            raise Exception("No hmm model!")
        backward_prob = [{}]
        for stat in self.states:
            backward_prob[0][stat] = self.stop_prob[stat]
        for i in range(1, len(obs)):
            backward_prob.append({})
            for stat in self.states:
                backward_prob[i][stat] = sum(
                    backward_prob[i-1][back_s] *
                    self.tran_prob[stat][back_s] *
                    self.emi_prob[back_s][obs[-i]]
                    for back_s in self.states)
        backward_prob.append({})
        for stat in self.states:
            backward_prob[-1][stat] = (self.start_prob[stat] *
                                       self.emi_prob[stat][obs[0]] *
                                       backward_prob[-2][stat])
        return sum(backward_prob[-1].values()), backward_prob

    def baum_welch(self, obsvervations, train_round=500):
        count = 0
        for _ in range(train_round):
            count += 1
            print("# NO.{} round training --".format(count))
            for obs in obsvervations:
                pre_tran = []
                pre_emi = []
                new_tran_prob = {}
                new_emi_prob = {}
                likely_hood, forward = self.forward_step(obs=obs)
                _, backward = self.backward_step(obs=obs)
                backward.reverse()
                for t in range(len(obs)):
                    tmp_emi, tmp_tran = {}, {}
                    for stat in self.states:
                        tmp_emi[stat] = {
                            "prob": np.divide(
                                forward[t][stat] * backward[t][stat], likely_hood
                            ),
                            "obs": obs[t]
                        }
                    pre_emi.append(tmp_emi)

                    for s_i in self.states:
                        tmp_tran[s_i] = {}
                        for s_j in self.states:
                            tmp_tran[s_i][s_j] = np.divide(
                                (forward[t][s_i] *
                                 self.tran_prob[s_i][s_j] *
                                 self.emi_prob[s_j][obs[t]] *
                                 backward[t+1][s_j]), likely_hood
                            )
                    pre_tran.append(tmp_tran)
                for s_i in self.states:
                    new_tran_prob[s_i] = {}
                    for s_j in self.states:
                        new_tran_prob[s_i][s_j] = np.divide(
                            sum([item[s_i][s_j] for item in pre_tran]),
                            sum([sum(item[s_i].values()) for item in pre_tran])
                        )
                for stat in self.states:
                    new_emi_prob[stat] = {}
                    denominator = sum([item[stat]["prob"] for item in pre_emi])
                    for o_i in obs:
                        numerator = sum([item[stat]["prob"] for item in pre_emi
                                         if item[stat]["obs"] == o_i])
                        new_emi_prob[stat][o_i] = np.divide(numerator, denominator)
            check_tran = self._is_convergence(new_prob=new_tran_prob,
                                              old_prob=self.tran_prob)
            check_emi = self._is_convergence(new_prob=new_emi_prob,
                                             old_prob=self.emi_prob)
            self.emi_prob = new_emi_prob
            self.tran_prob = new_tran_prob
            if check_tran and check_emi:
                print("First order hmm trained completely!")
                break

    def _has_model(self):
        if not self.tran_prob and not self.emi_prob:
            return False
        return True

    @staticmethod
    def _is_convergence(new_prob, old_prob):
        for row, col_info in new_prob.items():
            for col, value in col_info.items():
                diff = abs(old_prob[row][col]-value)
                if diff > 0.0001:
                    return False
        return True


