#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
コマンドライン引数のmp3ファイルをsplit_second秒ごとに分割し、そのファイルがあるディレクトリに
「split_file_*」というディレクトリを作成してその中に保存する

>>> python split_and_to_flac.py [file path] [split second]
"""

import os,sys
from os import makedirs
import subprocess

import glob2
from pydub import AudioSegment

args = sys.argv
file_path = args[1]
split_second = args[2]
dir_name = os.path.dirname(file_path)
base_name = os.path.basename(file_path)

# オーディオファイルを読み込み
print("loading {} ...".format(file_path))
song = AudioSegment.from_mp3(file_path)

length = len(song)  # 全体の長さ
all_seconds = float(length) / 1000  # 全体の長さ（秒単位）
split_size = split_second * 1000  # split_second秒で分割
num = int(float(length) / split_size) + 1  # 分割ファイル数
print("{} files will be made".format(num))


MP3_DIR = os.path.join(dir_name, "split_files_{}".format(base_name.split(".")[0]), "mp3")  # 分割したファイルの保存場所
if not os.path.exists(MP3_DIR):
    makedirs(MP3_DIR)
FLAC_DIR = os.path.join(dir_name, "split_files_{}".format(base_name.split(".")[0]), "flac")  # 変換したファイルの保存場所
if not os.path.exists(FLAC_DIR):
    makedirs(FLAC_DIR)
    
    

# 分割して保存

for i in range(num):
    start_second = i * split_size
    if i == (num-1):
        end_second = length
    else:
        end_second = (i+1) * split_size
    split_song = song[start_second: end_second]
    
    save_name = os.path.join(MP3_DIR, "split{}.mp3".format(i))
    
    split_song.export(save_name, format="mp3")
    print("{} saved".format(save_name))
    
print("spliting finished!")


# 分割したmp3をflacファイルに変換
for mp3 in glob2.glob(os.path.join(MP3_DIR, "*.mp3")):
    
    flac_name = os.path.basename(mp3).split(".")[0] + ".flac"
    flac_name = os.path.join(FLAC_DIR, flac_name)

    cmd = "sox {} --rate 16k --bits 16 --channels 1 {}".format(mp3, flac_name)
    result = subprocess.call(cmd, shell=True)  # 変換して保存
    
    if result == 0:
        print("{} saved".format(flac_name))
    else:
        print("{} failed".format(flac_name))

print("all finished!")
