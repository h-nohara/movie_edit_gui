#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys
from os import makedirs
import subprocess

import glob2
from pydub import AudioSegment



"""
音声ファイルを指定した秒ごとに分割し、その音声ファイルがあるディレクトリに
「split_file_*」というディレクトリを作成して、その中に分割した音声ファイルを保存する。
引数は以下の通り

$ python split_music.py [音声ファイル] [何秒で切り出すか] [出力の拡張子]

# 出力の拡張子:mp3かwav

example:
$ python split_music.py ../music.mp3 10.5 wav

もしくは
>>> from split_music import split_music
>>> split_music(file_path="../music.mp3", split_second=10.5, ext_output="wav")

pydubの詳細は
https://github.com/jiaaro/pydub/blob/master/API.markdown

"""


def split_music(file_path, split_second, ext_output):
    
    # 出力の拡張子を確認
    if (ext_output!="mp3") and (ext_output!="wav"):
        raise ValueError("output extention must be mp3 or wav")
    
    # path
    dir_name = os.path.dirname(file_path)
    base_name, ext = os.path.basename(file_path).split(".")


    # オーディオファイルを読み込み
    print("loading {} ...".format(file_path))

    # mp3
    if (ext=="mp3") or (ext=="MP3"):
        song = AudioSegment.from_mp3(file_path)
    # wav
    elif (ext=="wav") or (ext=="WAV"):
        song = AudioSegment.from_wav(file_path)
    # ogg
    elif (ext=="ogg") or (ext=="OGG"):
        song = AudioSegment.from_ogg(file_path)
    # flv
    elif (ext=="flv") or (ext=="FLV"):
        song = AudioSegment.from_flv(file_path)

    # 音声以外（ffmpeg support）
    # mp4
    elif (ext=="mp4") or (ext=="MP4"):
        song = AudioSegment.from_file(file_path, "mp4")
    # wma
    elif (ext=="wma") or (ext=="WMA"):
        song = AudioSegment.from_file(file_path, "wma")
    # aac
    elif (ext=="aac") or (ext=="AAC"):
        song = AudioSegment.from_file(file_path, "aac")



    # 分割するファイル数を計算
    length = len(song)  # 全体の長さ
    all_seconds = float(length) / 1000  # 全体の長さ（秒単位）
    split_size = split_second * 1000  # split_second秒で分割
    num = int(float(length) / split_size) + 1  # 分割ファイル数
    print("{} files will be made".format(num))


    RESULT_DIR = os.path.join(dir_name, "split_files_{}".format(base_name), ext_output)  # 分割したファイルの保存場所
    if not os.path.exists(RESULT_DIR):
        makedirs(RESULT_DIR)


    # 分割して保存

    for i in range(num):
        start_second = i * split_size
        if i == (num-1):
            end_second = length
        else:
            end_second = (i+1) * split_size
        split_song = song[start_second: end_second]
        
        save_name = os.path.join(RESULT_DIR, "{}_{:03d}.{}".format(base_name, i, ext_output))
        
        split_song.export(save_name, format=ext_output)
        print("{} saved".format(save_name))
        
    print("all finished!")


if __name__ == "__main__":
    
    # 引数の処理
    args = sys.argv
    file_path = args[1]
    split_second = float(args[2])
    ext_output = args[3]

    # 音声ファイルを分割する関数を実行
    split_music(file_path=file_path, split_second=split_second, ext_output=ext_output)

