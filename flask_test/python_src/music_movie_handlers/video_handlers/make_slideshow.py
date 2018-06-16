#!/user/bin/env python 
# -*- coding: utf-8 -*-

import os, sys, glob2
import subprocess, shutil
import numpy as np
import pandas as pd
from pandas import DataFrame, Series

from split_movie import split_one_movie, concat_movie
from get_length_of_video import get_length_of_video


def make_slideshow(movies, where_to_use, result_movie):
    
    '''
    複数の動画からスライドショーを作る。
    オリジナルの動画から一部を抜き出し　→　最初と最後にエフェクトをかける　→　それらの動画を結合
    '''
    
    assert len(movies) == len(where_to_use)

    # timelog秒かけてフェードアウト＋フェードインするコマンド
    temp_cmd = 'ffmpeg -y -i {original} -vf "fade=t=in:st=0:d={timelong_feedin}, fade=t=out:st={starttime_feedout}:d={timelong_feedout}" {result}'
    
    # 分割した動画を一時的に保存するディレクトリを作成する
    dir_name = os.path.dirname(result_movie)
    temporal_dir = os.path.join(dir_name, "_temporal")
    if os.path.exists(temporal_dir):
        shutil.rmtree(temporal_dir)
    os.makedirs(temporal_dir)
    
    for i, mp in enumerate(zip(movies, where_to_use)):
        
        movie, position = mp
        split_movie = os.path.join(temporal_dir, "split{0:03d}.mp4".format(i))  # 分割した後の動画の名前
        split_one_movie(original_movie=movie, where_to_cut=position, result_movie=split_movie)  # 動画を分割
        
        # フェードイン・フェードアウトのエフェクトをつける
        length = get_length_of_video(split_movie)  # 動画の長さを取得
        
        timelong_feedin = 1 if i==0 else 0.5
        timelong_feedout = 1 if i==len(movies)-1 else 0.5
        starttime_feedout = length - timelong_feedout
        starttime_feedout = round(starttime_feedout, 3)

        cmd = temp_cmd.format(
            original = split_movie,
            timelong_feedin = timelong_feedin,
            starttime_feedout = starttime_feedout,
            timelong_feedout = timelong_feedout,
            result = os.path.join(temporal_dir, "effected_split{0:03d}.mp4".format(i))
        )

        print(cmd)
        #sys.exit()
        ret = subprocess.call(cmd, shell=True)
        assert ret == 0

    # 動画を連結
    effected_movies = sorted(glob2.glob(os.path.join(temporal_dir, "effected_split*.mp4")))
    concat_movie(movies=effected_movies, result_movie=result_movie)

    # 一時的なフォルダを削除
    shutil.rmtree(temporal_dir)
