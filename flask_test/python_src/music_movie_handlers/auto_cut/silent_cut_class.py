#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os,sys
import glob2
import numpy as np
from numpy.random import randint
import pandas as pd
from pandas import DataFrame, Series
import matplotlib.pyplot as plt

import cv2
import soundfile as sf


class SilentCutClass():
    
    '''
    sound = SilentCutClass("./sample.wav")
    sound.read()
    sound.detect_silent()
    sound.save_cut_sound("./output.wav")
    '''
    
    def __init__(self, fname):
        
        self.fname = fname
        
        self.data = None
        self.samplerate = None
        
        self.length_ms = None
        self.length_second = None
        self.length_min = None
        
        self.silent_judge_final = None
        self.silent_mask = None
        
        
    def read(self):
        
        # 音声ファイルの読み込み
        
        self.data, self.samplerate = sf.read(self.fname)
        self.data = np.array(self.data)
        self.length_ms = self.data.shape[0]
        self.length_second = self.data.shape[0] / self.samplerate
        self.length_min = self.length_second / 60
        
        print("data.shape  :   {}".format(self.data.shape))
        print("samplerate  :  {}".format(self.samplerate))
        print("length  :  {} 分".format(self.length_min))
        
    
    def plot(self, col=0):
        
        # 読み込んだ音声ファイルを可視化
        # colで何列目を可視化するか指定
        
        if len(self.data.shape) == 1:
            plt.plot(self.data)
        
        else:
            plt.plot(self.data[:, col])
        
        plt.show()
        
    def detect_silent(self, block_size=1.0, slide_size=0.1, threshold=0.2, col=0):
        
        '''
        引数は全て秒単位
        block_size : ブロックサイズを1秒（１秒以上無音が続いたら削除）
        slide_size : 0.1秒のギャップを許す（ブロックのスライド間隔）
        threshold : 絶対値が0.2以下を無音とみなす
        '''
        
        blocksize_ms = int(block_size * self.samplerate)
        slide_ms = int(slide_size * self.samplerate)
        overlap_ms = blocksize_ms - slide_ms
        
        print(blocksize_ms)
        print(slide_ms)
        print(overlap_ms)
        
        
        # silent_listを作る
        silent_judge = []  # ０なら無音、１なら有音
        i = 0
        for block in sf.blocks(self.fname, blocksize=blocksize_ms, overlap=overlap_ms):
            
            if len(block.shape) == 1:
                block = abs(block)
                if len(block) != blocksize_ms:
                    length_last_block = len(block)
                    print("last")
                    print(length_last_block)
                else:
                    length_last_block = 0
            else:
                block = abs(block[:, col])
                if len(block) != blocksize_ms:
                    length_last_block = len(block)
                    print("last")
                    print(length_last_block)
                else:
                    length_last_block = 0
            
            binal_arr = np.where(block > threshold, 1, 0)  # 絶対値が0.2以上は1, 未満は0の行列

            if np.sum(np.ones(len(binal_arr)) * binal_arr) == 0:
                silent_judge.append(0)
            else:
                silent_judge.append(1)

            i += 1
            
                        
        
        # silent_listから実際の長さと合うような無音判定行列を作る
        final_silent_judge = []
        
        for i in range(len(silent_judge)):
            
            val = silent_judge[i]
            
            if val == 0:
                if i == len(silent_judge) - 1:
                    final_silent_judge.append([0]*length_last_block)
                else:
                    final_silent_judge.append([0]*slide_ms)
            elif val == 1:
                if i == len(silent_judge) - 1:
                    final_silent_judge.append([1]*length_last_block)
                else:
                    final_silent_judge.append([1]*slide_ms)
            
#         silent_judge = []
#         for smll in new_listing:
#             for val in smll:
#                 silent_judge.append(val)
                
#         silent_judge_final = np.ones(self.length_ms)
#         silent_judge_final[:len(silent_judge)] = silent_judge

        final_silent_judge_flatten = []
        for blk in final_silent_judge:
            for num in blk:
                final_silent_judge_flatten.append(num)
        
        self.silent_judge_final = np.array(final_silent_judge_flatten)
        self.silent_mask = np.array(final_silent_judge_flatten) == 1
        
        
    def plot_silent_judge(self, col=0):
        
        
        if len(self.data.shape) == 1:
            plt.plot(self.data)
            max_val = max(self.data)
        else:
            plt.plot(self.data[:, col])
            max_val = max(self.data[:, col])
        
        print(max_val)
            
        plt.plot(self.silent_judge_final * max_val)
            
        plt.show()
        
    
    def save_cut_sound(self, outname, col=0):
        
        if len(self.data.shape) == 1:
            output = self.data[self.silent_mask]
        else:
            output = self.data[:, col][self.silent_mask]
            
        print("{} => {}".format(self.data.shape, output.shape))
            
        sf.write(outname, output, self.samplerate)
