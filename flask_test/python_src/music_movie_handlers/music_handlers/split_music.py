#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, subprocess, glob2, shutil
import numpy as np

'''
soxを使って音声ファイルを　トリミング/結合
'''


def split_one_music(original_music, where_to_cut, result_music):
    
    '''
    soxを使って音声ファイルをトリミング

    >>> split_one_music(original.mp3, [3, 5.6], result.wav)
    '''
    
    start_time = where_to_cut[0]
    end_time = where_to_cut[1]
    timelong = end_time - start_time

    cmd = "sox {} {} trim {} {}".format(original_music, result_music, start_time, timelong)
    print(cmd)

    ret = subprocess.call(cmd, shell=True)
    assert ret == 0
    print("saved {}".format(result_music))


def split_music(original_music, where_to_cut, save_dir, save_ext=None):
    
    '''
    soxを使って音声ファイルを複数に分割
    
    >>> split_music("original.wav", [[0,3], [5,10], [12,12.4]], "here/")
    '''

    # 分割されたファイルの保存ディレクトリを作成
    if os.path.exists(save_dir):
        shutil.rmtree(save_dir)
    os.makedirs(save_dir)


    # 分割するファイルの拡張子を決定（デフォルトでは元と同じ拡張子で保存）
    if save_ext is None:
        ext = os.path.basename(original_music).split(".")[-1]
    else:
        ext = save_ext


    for i, pos in enumerate(where_to_cut):
        
        assert len(pos) == 2
        start_time = pos[0]
        end_time = pos[1]

        mini_music = os.path.join(save_dir, "split{number:03d}.{ext}".format(number=i, ext=ext))

        split_one_music(original_music=original_music, where_to_cut=[start_time, end_time], result_music=mini_music)

    print("all split finished!")



def concat_music(musics, result_music):
    
    '''
    複数の音声ファイルを結合する
    '''
    
    all_music = ""
    for music in musics:
        all_music += "{} ".format(music)

    cmd = "sox {} {}".format(all_music, result_music)
    print(cmd)

    ret = subprocess.call(cmd, shell=True)
    assert ret == 0
    print("saved {}".format(result_music))

        