#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2017/12/22 14:30
# @Author  : BigDin
# @Contact : dinglei_1107@outlook.com

states = ('Healthy', 'Fever')

observations = ('normal', 'cold', 'dizzy')

start_probability = {'Healthy': 0.6, 'Fever': 0.4}

transition_probability = {
    'Healthy': {'Healthy': 0.7, 'Fever': 0.3},
    'Fever': {'Healthy': 0.4, 'Fever': 0.6},
}

emission_probability = {
    'Healthy': {'normal': 0.5, 'cold': 0.4, 'dizzy': 0.1},
    'Fever': {'normal': 0.1, 'cold': 0.3, 'dizzy': 0.6},
}


if __name__ == "__main__":
    from hmm.HMM import FirstOrderHMM

    tran1 = {
        'Healthy': {'Healthy': 0.6, 'Fever': 0.4},
        'Fever': {'Healthy': 0.4, 'Fever': 0.6},
    }

    emi1 = {
        'Healthy': {'normal': 0.4, 'cold': 0.3, 'dizzy': 0.3},
        'Fever': {'normal': 0.2, 'cold': 0.4, 'dizzy': 0.4},
    }

    obs1 = {
        ('normal', 'normal', 'cold', 'cold', 'dizzy', 'dizzy', 'normal'),
        ("normal", "dizzy", "cold"),
        ("cold", "dizzy", "normal"),
    }

    hmm_model = FirstOrderHMM()
    hmm_model.load_hmm(
        tran_prob=tran1,
        emi_prob=emi1
    )
    hmm_model.baum_welch(obsvervations=obs1)
    print("转移概率矩阵: {}".format(hmm_model.tran_prob))
    print("映射概率矩阵: {}".format(hmm_model.emi_prob))
    # print(
    #     hmm_model.viterbi_step(obs=observations)
    # )
    # print(hmm_model.forward_step(obs=observations))
    # print(hmm_model.backward_step(obs=observations))

