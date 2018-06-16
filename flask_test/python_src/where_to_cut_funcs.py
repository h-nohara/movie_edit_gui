#!/user/bin/env python 
# -*- coding: utf-8 -*-

import os, sys, glob2
import numpy as np
import pandas as pd
from pandas import DataFrame, Series


def check_where_to_split(df, span):

    '''
    [[index,      "start_time", "end_time"],
     ["これは" ,           0,        3.0],
     ["最初",            3.0,        5.0],
     ["の",              6.5,        7.0],
     ["文章",             7.5,        9.0],
     ["です",             9.0,       10.0]]
    のようなデータフレームを入力にする。
    改行判定用の["is_split"]カラムを付け足す（0ならそのまま、1ならその単語の先頭で改行。
    spanが1.0なら"の"の位置で改行判定を入れる。

    :param pandas.DataFrame df: 元のデータフレーム
    :param float span: この秒数以上間が空いたら分割

    :return pandas.DataFrame: "is_split"カラムを加えた結果のデータフレーム
     
    '''

    df.loc[:, "is_split"] = np.zeros(df.shape[0])

    before_endtime = None
    is_split = []

    for i in range(df.shape[0]):

        row = df.iloc[i]
        start_time = row["start_time"]
        end_time = row["end_time"]

        if i != 0:
            if (start_time - before_endtime) <= span:
                is_split.append(0)
            else:
                is_split.append(1)
        else:
            is_split.append(0)
        
        before_endtime = end_time

    df.loc[:, "is_split"] = is_split
    df = df[["start_time", "end_time", "is_split"]]

    return df


def split_and_to_block(df):

    '''
    [["",      "start_time", "end_time", "is_split"],
     ["これは" ,           0,        3.0,          0],
     ["最初",            3.0,        5.0,          0],
     ["の",              6.5,        7.0,          1],
     ["文章",             7.5,        9.0,         0],
     ["です",             9.0,       10.0,         0]]
    のようなデータフレームを入力にする。
    "is_split"を元に、ブロックごとにまとめる

    :param pandas.DataFrame df: 元のデータフレーム

    :return pandas.DataFrame: 分割ブロックごとにまとめたデータフレーム
     
    '''

    df.loc[:, "word"] = list(df.index)
    df = df.reset_index(drop=True)

    temporal_words = None
    temporal_start_time = None
    dataframe_batches = []

    for i in range(df.shape[0]):
        
        row = df.iloc[i]
        word = row["word"]
        start_time = row["start_time"]
        end_time = row["end_time"]
        is_split = row["is_split"]


        # 最初の行
        if i == 0:
            temporal_start_time = start_time
            temporal_words = word

        
        # 最後の行
        elif i == df.shape[0]-1:
            if is_split == 0:
                dataframe_batches.append(
                    DataFrame(
                        data = {"start_time":temporal_start_time, "end_time":end_time},  # 最後まで
                        index = [temporal_words]
                        )
                    )
            else:
                dataframe_batches.append(
                    DataFrame(
                        data = {"start_time":temporal_start_time, "end_time":df.iloc[i-1]["end_time"]},  # １個手前のend_timeまで
                        index = [temporal_words]
                        )
                    )
                dataframe_batches.append(
                    DataFrame(
                        data = {"start_time":start_time, "end_time":end_time},  # 最後の行だけ
                        index = [temporal_words]
                        )
                    )

        # それ以外
        else:
            if is_split == 0:
                temporal_words += word
            else:
                dataframe_batches.append(
                    DataFrame(
                        data = {"start_time":temporal_start_time, "end_time":df.iloc[i-1]["end_time"]},
                        index = [temporal_words]
                        )
                    )
                temporal_start_time = start_time
                temporal_words = word


    result_df = pd.concat(dataframe_batches)
    result_df = result_df[["start_time", "end_time"]]
    return result_df



def transform_for_working_table(df):
    
    '''
    :param pandas.DataFrame df: インデックスがword, [start_time, end_time]の２カラムがあるデータフレーム
    '''
    
    cols = df.columns
    assert ("start_time" in cols) and ("end_time" in cols)

    num_rows = df.shape[0]

    # デフォルトの値を設定
    df.loc[:, "is_use"] = [1] * num_rows
    df.loc[:, "is_telop"] = [0] * num_rows
    df.loc[:, "telop_word"] = list(df.index)
    df.loc[:, "font"] = ["hiragino"] * num_rows
    df.loc[:, "fontsize"] = [120] * num_rows
    df.loc[:, "color"] = ["pink_white_pink"] * num_rows

    df = df[["start_time", "end_time", "is_use", "is_telop", "telop_word", "font", "fontsize", "color"]]

    return df




if __name__ == "__main__":

    # df = pd.read_csv("./result.csv", index_col=0)
    # result_df = check_where_to_split(df, 0.1)

    # result_df.to_csv("./result_judged.csv")

    df = pd.read_csv("./result_judged.csv", index_col=0)
    result_df = split_and_to_block(df)
    result_df.to_csv("./result_block.csv")
