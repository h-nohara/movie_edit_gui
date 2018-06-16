#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

import cv2
from PIL import Image
import soundfile as sf

from .silent_cut_class import SilentCutClass
from ..video_handlers.mp4_to_sound import mp4_to_sound

def normalize(the_data):
    M = 1
    m = -1
    normalized = ((the_data - the_data.min()) /  (the_data.max() - the_data.min())) * (M - m) + m
    return normalized


class MovieCutClass():
    
    def __init__(self, fname):
        
        # 動画を読み込む
        self.fname = fname
        self.base_name = os.path.basename(fname).split(".")[0]
        self.save_dir = os.path.join(os.path.dirname(self.fname), self.base_name)
        self.video = cv2.VideoCapture(self.fname)
        
        # 読み込んだ動画の情報を表示
        self.video_frame_count = int(self.video.get(7)) #フレーム数を取得
        self.video_frame_rate = int(self.video.get(5))  #フレームレート(1秒間に何コマあるか)を取得
        self.video_length_s = self.video_frame_count / self.video_frame_rate # 全体の長さ
        
        self.print_video_information()
        
        
        self.music_name = None  # 変換したmp3の名前
        self.music = None
        self.music_class = None
        
        self.sound_all_ind = None
        self.where_to_cut = None
        
        self.split_movie_dir = None
        
    def print_video_information(self):
        
        print("====== infromation ======")
        print("frame count : {}".format(self.video_frame_count))
        print("frame rate : {}".format(self.video_frame_rate))
        print("length(s) : {} s".format(round(self.video_length_s, 2)))  # 全体の時間（秒）
        print("=====================")
        
        
    def video2music(self):
        
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
            
        self.music_name = os.path.join(self.save_dir, self.base_name+".wav")
#        cmd = "ffmpeg -y -i {} -ab 128k {}".format(self.fname, self.music_name)
#        subprocess.call(cmd, shell=True)
        mp4_to_sound(input_file=self.fname, output_file=self.music_name)
        print("{} saved".format(self.music_name))
        
    
    def read_music(self, plot=True, col=0):
        
        self.music_class = SilentCutClass(self.music_name)
        self.music_class.read()
        self.music = self.music_class.data
        
        if plot:
            self.music_class.plot(col=col)
            
        
    def detect_silent(self, block_size=1.0, slide_size=0.1, threshold=0.02, col=0, plot=False):
        
        self.music_class.detect_silent(block_size=block_size, slide_size=slide_size, threshold=threshold, col=col)
        
        if plot:
            self.music_class.plot_silent_judge(col=col)
        
        
        
    def decide_where_to_cut(self):
        
        sound_mask = self.music_class.silent_judge_final
        sound_samplerate = self.music_class.samplerate
        sound_interval_ms = (1. / sound_samplerate) * 1000
        
        df_sound = DataFrame(sound_mask, np.arange(len(sound_mask))*sound_interval_ms, columns=["sound_mask"])
        #df_sound["is_sound"] = 1
        
        all_ind = list(df_sound.index)
        self.sound_all_ind = all_ind
        listing = []
        arr_listing = []

        
        # [0,1]になっている点（使わない部分→使う部分）と[1,0]のindexを取得

        for i in range(len(all_ind)-1):
            arr = np.array([sound_mask[i], sound_mask[i+1]])
            arr_listing.append(arr)
        
        arr_listing.append([sound_mask[-1], sound_mask[-1]])
        arr_concat = np.c_[arr_listing]
        df_concat = DataFrame(arr_concat)
        df_concat.index = all_ind
        df_concat.columns = ["mask", "next_mask"]
        df_concat["sum"] = list(df_concat.sum(axis=1))
        
        df_concat_change_point = df_concat[df_concat["sum"]==1].astype(float) 
        
        start_end_list = []
        start_end = []
        for ind in df_concat_change_point.index:
            if (df_concat_change_point.loc[ind, "mask"] == 0) and (df_concat_change_point.loc[ind, "next_mask"] == 1):
                start_end.append(ind)
            elif (df_concat_change_point.loc[ind, "mask"] == 1) and (df_concat_change_point.loc[ind, "next_mask"] == 0):
                start_end.append(ind)
                
                start_end_list.append(list(np.array(start_end, dtype=float)/1000))
                start_end = []
                
        if start_end != []:  # 動画が無音でない状態で終わる場合
            start_end_list.append([start_end[0], self.sound_all_ind[-1]])
        if len(start_end_list[0]) == 1:  # 動画の最初から使う場合（無音でない状態から始まる場合に備えて）
            start_end_list[0] = [0, start_end_list[0][0]]            
                
        print(start_end_list)
        
        self.where_to_cut = start_end_list

        
    
    def split_movie(self, pre=0, post=0):
        
        # シェルコマンドで動画を分割
        
        self.split_movie_dir = os.path.join(self.save_dir, "split_movies")  # 分割した動画を保存する場所
        if not os.path.exists(self.split_movie_dir):
            os.makedirs(self.split_movie_dir)
        
        cmd_temp = "ffmpeg -ss {} -i {} -t {} {}"
        
        i = 0
        
        for i, l in enumerate(self.where_to_cut):

            s_original = float(l[0])
            s = round(s_original, 4) - pre
            e_original = float(l[1])
            e = round(l[1], 4) + post
            
            timelong = round((e_original - s_original), 4)
            cmd = cmd_temp.format(s, self.fname, timelong, os.path.join(self.split_movie_dir, "output{}.mp4".format(i)))

            print(cmd)

            subprocess.call(cmd, shell=True)

        print("cut finished")
        
        
    def concat_movie(self):
        
        # 分割した動画をつなぎ合わせる
        
        num = len(glob2.glob(os.path.join(self.split_movie_dir, "*.mp4")))
        with open("./split_files.txt", "a") as f:
            for i in range(num):
                t = os.path.join("file '{}'".format(os.path.join(self.split_movie_dir, "output{}.mp4".format(i))))
                f.write(t)
                f.write("\n")
                
        concat_cmd = "ffmpeg -f concat -safe 0 -i {} -c copy {}".format("./split_files.txt", os.path.join(self.save_dir, "concated.mp4"))   
        
        subprocess.call(concat_cmd, shell=True)
        
        
    def remove(self):
        
        os.remove("./split_files.txt")
        os.remove(self.music_name)
        shutil.rmtree(self.split_movie_dir)
        
        
    def do_all(self, block_size=0.40, threshold=0.05):
        
        s = time.time()
        
        self.video2music()
        self.read_music(plot=False)
        self.music_class.data = normalize(self.music[:, 0])
        plt.plot(self.music_class.data)
        plt.show()
        # パラメータを決める
        self.detect_silent(block_size=block_size, threshold=threshold)
        self.decide_where_to_cut()
        self.split_movie()
        self.concat_movie()
        self.remove()
        
        e = time.time()
        print("spent {} s".format(str(e-s)))

