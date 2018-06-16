#!/user/bin/env python 
#-*-coding:utf-8-*-

import os,sys
from os import makedirs
import shutil
import time
import copy
import glob2
import subprocess
import numpy as np
from numpy.random import randint
import pandas as pd
from pandas import DataFrame, Series
import matplotlib.pyplot as plt



def split_one_movie(original_movie, where_to_cut, result_movie):
    
    # シェルコマンドで動画を一回だけ分割
    
    cmd_temp = "ffmpeg -y -ss {} -i {} -t {} {}"

    s = round(float(where_to_cut[0]), 4)
    e = round(float(where_to_cut[1]), 4)
        
    timelong = round((e - s), 4)
    cmd = cmd_temp.format(s, original_movie, timelong, result_movie)
    print(cmd)

    ret = subprocess.call(cmd, shell=True)
    assert ret==0


def split_movie(original_movie, where_to_cut):
        
    # シェルコマンドで動画を複数に分割
    
    split_movie_dir = os.path.join(os.path.dirname(original_movie), "split_movies")  # 分割した動画を保存する場所
    if not os.path.exists(split_movie_dir):
        os.makedirs(split_movie_dir)
    
    cmd_temp = "ffmpeg -y -ss {} -i {} -t {} {}"
    
    i = 0
    
    for l in where_to_cut:

        s = round(float(l[0]), 4)
        e = round(float(l[1]), 4)
        
        timelong = round((e - s), 4)
        cmd = cmd_temp.format(s, original_movie, timelong, os.path.join(split_movie_dir, "split{0:03d}.mp4".format(i)))

        print(cmd)

        subprocess.call(cmd, shell=True)
        i += 1

    print("cut finished")
        
        
def concat_movie(movies, result_movie):
    
    save_dir = os.path.dirname(result_movie)
    textfile = os.path.join(save_dir, "split_movies.txt")

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # 分割した動画をつなぎ合わせる

    split_movies = movies
    
    with open(textfile, "w") as f:
        for movie in split_movies:
            t = os.path.join("file '{}'".format(os.path.abspath(movie)))
            f.write(t)
            f.write("\n")
            
    concat_cmd = "ffmpeg -y -f concat -safe 0 -i {} -c copy {}".format(textfile, result_movie)

    print(concat_cmd)
    ret = subprocess.call(concat_cmd, shell=True)

    # 削除
    if ret == 0:
        os.remove(textfile)
    else:
        sys.exit()
        
        
