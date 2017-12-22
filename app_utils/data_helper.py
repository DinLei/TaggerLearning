#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2017/12/18 17:19
# @Author  : BigDin
# @Contact : dinglei_1107@outlook.com


def dim_reduce4train(db_type="sqlite_config", keep_dim=500,
                     max_features=8000, ngram_range=(1, 3), scale_type="max_min"):
    import numpy as np
    import pandas as pd
    from app_utils.db_util import DbConn
    from app_utils.matrix_operator import MatDimReduction, MatrixOperation
    from app_utils.text_operator import text_vector_model, text2vec, one_hot_encoder
    db_conn = DbConn(db_type=db_type)
    sale_df = pd.read_sql_query(
        """
            SELECT 
            jan,
            feb,
            mar,
            apr,
            may,
            jun,
            jul,
            aug,
            sep,
            oct,
            nov,
            dec
            FROM nlp_training_data;
        """, db_conn.conn
    )
    desc_df = pd.read_sql_query(
        """
            SELECT title, product, details, function, shoulder, 
            sleeve, design, style, neck, hem, fit FROM nlp_training_data;
        """, db_conn.conn
    )
    label_df = pd.read_sql_query(
        """
            SELECT is_spring, is_summer, is_autumn, is_winter FROM nlp_training_data;
        """, db_conn.conn
    )
    t2v_model = text_vector_model(desc_df["title"],
                                  max_features=max_features,
                                  ngram_range=ngram_range)
    matrix = text2vec(texts=desc_df["title"], t2v_model=t2v_model)
    feats = t2v_model.get_feature_names()
    title_df = pd.DataFrame(
        [pd.SparseSeries(matrix[i].toarray().ravel())
         for i in np.arange(matrix.shape[0])]
    )
    title_df.columns = feats
    attr_df = one_hot_encoder(desc_df, del_cols=["title"])
    feats_df = pd.concat([title_df, attr_df], axis=1)
    feats_mat = feats_df.as_matrix()
    print("降维前描述数据矩阵size: {}".format(feats_mat.shape))

    dim_reduce = MatDimReduction(feats_mat)
    dim_reduce_mat, pca_model = dim_reduce.compress_with_pca(keep_dim=keep_dim)
    print("降维后描述数据矩阵size: {}".format(dim_reduce_mat.shape))

    # sale_mat = MatrixOperation.mat_normalization(
    #     matrix=sale_df.as_matrix(), scale_type=scale_type
    # )
    # print("销售数据矩阵size: {}".format(sale_mat.shape))
    # new_mat = np.hstack((sale_mat, dim_reduce_mat))
    # print("最终组合矩阵size: {}".format(new_mat.shape))
    # return new_mat, label_df.as_matrix(), pca_model, t2v_model, attr_df.columns
    return dim_reduce_mat, label_df.as_matrix(), pca_model, t2v_model, attr_df.columns
    # return dim_reduce_mat, label_df.as_matrix(), pca_model, t2v_model, attr_df.columns


def data_splits(x_matrix, y_vector,
                test_size=0.3,
                random_state=0,
                shuffle=True):
    from sklearn.model_selection import train_test_split
    return train_test_split(
        x_matrix, y_vector,
        test_size=test_size,
        random_state=random_state,
        shuffle=shuffle
    )


def recall(truth, predict):
    nume = 0
    nrow, ncol = truth.shape
    for ind, true in enumerate(truth):
        pred = predict[ind]
        if sum((true-pred)>=0) == ncol:
                nume += 1
    return nume/nrow


if __name__ == "__main__":
    from sklearn.multiclass import OneVsRestClassifier
    from sklearn.multiclass import OneVsOneClassifier
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.multioutput import MultiOutputClassifier
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.svm import LinearSVC, SVC

    clf1 = OneVsRestClassifier(SVC(kernel='linear'), n_jobs=-1)
    clf2 = OneVsRestClassifier(LogisticRegression(), n_jobs=-1)

    # multi_target_forest = MultiOutputClassifier(SVC(kernel="rbf"), n_jobs=-1)

    for l in [2000]:
        print("dim: {}".format(l))
        model = clf2

        mat, label, _, _, _ = dim_reduce4train(keep_dim=l,
                                               max_features=None)

        X_train, X_test, y_train, y_test = data_splits(mat, label)

        model.fit(X_train, y_train)
        print("训练完成")
        predict_class = model.predict(X_test)
        print("预测完成")
        print("linear准确率: {}".format(model.score(X_test, y_test)))
        print("linear召回率: {}".format(recall(y_test, predict_class)))




