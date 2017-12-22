#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2017/9/29 14:16
# @Author  : BigDin
# @Contact : dinglei_1107@outlook.com


import heapq
import numpy as np
from scipy.sparse import csr, linalg


def nlargest_index(arr, top_n=1):
    if isinstance(arr, np.ndarray):
        arr = arr.tolist()[0]
    assert isinstance(arr, list)
    assert isinstance(top_n, int) and top_n >= 0
    assert len(arr) > 0
    top_n = min(len(arr), top_n)
    new_arr = list(zip(range(len(arr)), arr))
    new_arr = sorted(new_arr, key=lambda e: e[1], reverse=True)
    return [x[0] for x in new_arr][:top_n]


class MatDimReduction:
    """
    简单的对稠密矩阵进行SVD和PCA两种降维方式
    """
    def __init__(self, matrix):
        assert isinstance(matrix, np.ndarray)
        self._mat = matrix

    def compress_with_svd(self, keep_dim=1):
        """
        奇异值分解
        :param keep_dim: 需要降低到的维度
        :return: 
        """
        nrow, ncol = self._mat.shape
        assert nrow >= 1 and ncol >= 1 and keep_dim <= ncol
        print("Option:[SVD]. Matrix dim:({}, {})".format(nrow, ncol))
        mat_u, list_s, _ = np.linalg.svd(self._mat)
        return np.dot(mat_u[:, :keep_dim], np.diag(list_s[:keep_dim]))

    def compress_with_pca(self, keep_dim=1):
        """
        PCA降维
        :param keep_dim: 需要降低到的维度
        :return: 
        """
        nrow, ncol = self._mat.shape
        if ncol < keep_dim:
            keep_dim = ncol
        from sklearn.decomposition import PCA
        pca = PCA(n_components=keep_dim)
        print("\tOption:[PCA]. Matrix dim:({}, {})".format(nrow, ncol))
        return pca.fit_transform(self._mat), pca


class MatrixOperation:
    """
    提供矩阵归一化和余弦相似度计算
    """
    def __init__(self, matrix):
        assert isinstance(matrix, csr.csr_matrix) or isinstance(matrix, np.ndarray)
        self._mat = matrix

    # 矩阵归一化处理
    @staticmethod
    def mat_normalization(matrix, scale_type="normalize", log=True, axis=1):
        """
        数据归一化
        :return: 返回归一化后的矩阵
        """
        assert isinstance(matrix, csr.csr_matrix) or isinstance(matrix, np.ndarray)
        print("\tNormalizing, [{}]...".format(scale_type))
        if scale_type == "max_min":
            from sklearn.preprocessing import minmax_scale
            normalizer = minmax_scale
        elif scale_type == "z_score":
            from sklearn.preprocessing import scale
            normalizer = scale
        elif scale_type == "normalize":
            from sklearn.preprocessing import normalize
            normalizer = normalize
        else:
            return matrix
        if log:
            matrix = np.log(1 + matrix)
        return normalizer(matrix, axis=axis)

    @staticmethod
    def cos_similarity(matrix):
        """
        对矩阵计算余弦相似度
        :return: 余弦相似度分数
        """
        assert isinstance(matrix, csr.csr_matrix) or isinstance(matrix, np.ndarray)
        print("Computing similarity...")
        nrow, ncol = matrix.shape
        numerator = np.dot(matrix, matrix.T)
        if isinstance(matrix, csr.csr_matrix):
            tmp = linalg.norm(matrix, axis=1)
        else:
            tmp = np.linalg.norm(matrix, axis=1)
        tmp2mat = np.reshape(tmp, (len(tmp), 1))
        denominator = np.dot(tmp2mat, tmp2mat.T) + 0.0000001
        cos_matrix = numerator / denominator
        cos_matrix = cos_matrix.astype(float)
        cos_matrix = cos_matrix - np.eye(nrow)
        return 0.5 + 0.5 * cos_matrix

    @staticmethod
    def cos_similarity2(mat1, mat2):
        """
        对矩阵计算余弦相似度
        :return: 余弦相似度分数
        """
        assert isinstance(mat1, csr.csr_matrix) or isinstance(mat1, np.ndarray)
        assert isinstance(mat2, csr.csr_matrix) or isinstance(mat2, np.ndarray)
        print("Computing similarity...")
        numerator = np.dot(mat1, mat2.T)
        if isinstance(mat1, csr.csr_matrix):
            tmp1 = linalg.norm(mat1, axis=1)
        else:
            tmp1 = np.linalg.norm(mat1, axis=1)
        if isinstance(mat2, csr.csr_matrix):
            tmp2 = linalg.norm(mat2, axis=1)
        else:
            tmp2 = np.linalg.norm(mat2, axis=1)
        tmp12mat = np.reshape(tmp1, (len(tmp1), 1))
        tmp22mat = np.reshape(tmp2, (len(tmp2), 1))
        denominator = np.dot(tmp12mat, tmp22mat.T) + 0.0000000001
        cos_matrix = numerator / denominator
        cos_matrix = cos_matrix.astype(float)
        return 0.5 + 0.5 * cos_matrix

    @staticmethod
    def top_n_indexes(score_mat, top_n=3, to_array=True, n_largest_func=nlargest_index):
        """
        矩阵按行返回TOP_N个最大值的索引
        :param score_mat: 
        :param top_n: 
        :param n_largest_func: 
        :param to_array: 
        :return: 
        """
        assert isinstance(score_mat, np.ndarray)
        print("Getting top {}...".format(top_n))
        nrow, ncol = score_mat.shape
        print("Score mat shape:【{}, {}】".format(nrow, ncol))
        per01 = 100
        assert isinstance(top_n, int)
        if top_n >= ncol:
            top_n = ncol
        outcome = []
        for i in range(nrow):
            if i % per01 == 0:
                print("Having complete recommend {:0.2f}%".format((i/nrow)*100))
            if n_largest_func:
                top_n_ind = n_largest_func(score_mat[i], top_n)
            else:
                top_n_ind = heapq.nlargest(
                    top_n, range(ncol), score_mat[i].take)
            outcome.append(top_n_ind)
        if to_array:
            return outcome
        return np.array(outcome)


