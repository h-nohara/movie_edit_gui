#!/user/bin/env python 
# -*- coding: utf-8 -*-

'''無音判定データフレームを作成する'''

import os,sys, shutil
import glob2
import subprocess
from decimal import Decimal, ROUND_HALF_UP
import numpy as np
import pandas as pd
from pandas import DataFrame, Series
import matplotlib.pyplot as plt


from .music_movie_handlers.auto_cut.movie_cut_class import MovieCutClass, normalize

def make_silent_judge_dataframe(original_movie, result_csv, block_size=0.3, threshold=0.02):

    mcc = MovieCutClass(fname=original_movie)
    mcc.video2music()
    mcc.read_music(plot=False)
    mcc.music_class.data = normalize(mcc.music)

    # 無音判定＋プロット
    plt.figure(figsize=(18,5))
    mcc.detect_silent(block_size=block_size, threshold=threshold, plot=False)

    mcc.decide_where_to_cut()
    where_to_cut = []
    for chunk in mcc.where_to_cut:
        s = Decimal(chunk[0]).quantize(Decimal("0.000"), rounding=ROUND_HALF_UP)
        e = Decimal(chunk[1]).quantize(Decimal("0.000"), rounding=ROUND_HALF_UP)
        where_to_cut.append((float(s), float(e)))

    df = DataFrame(
        {
            "start_time":[chunk[0] for chunk in where_to_cut],
            "end_time":[chunk[1] for chunk in where_to_cut],
        },
    )

    df.index = ["hoge"] * df.shape[0]
    df = df[["start_time", "end_time"]]
    df.to_csv(result_csv)
        
