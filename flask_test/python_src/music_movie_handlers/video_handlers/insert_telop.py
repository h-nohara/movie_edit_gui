#!/user/bin/env python 
# -*- coding: utf-8 -*-

import os, sys, subprocess
import glob2
import numpy as np
import pandas as pd
from pandas import DataFrame, Series
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import cv2


fontfile_sample = "/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc"


def insert_telop(original_movie, result_movie, fontfiles, texts, fontsizes, fontcolors, xs, ys, ss, es):
    
    '''
    １つの動画に複数のテロップを入れる関数

    original_movie : テロップを差し込む動画
    result_movie : 生成する動画名

    * 以下はそれぞれテロップ数と同じ長さのリスト
    fontfiles : フォントファイル
    texts : 文字
    fontsizes : フォントサイズ
    fontcolors : 文字の色
    xs : テロップ（の左上）のx座標の位置
    ys : テロップ（の左上）のy座標の位置
    ss : 開始位置（秒）
    es : 終了位置（秒）

    '''
    
    the_instance = SubtitleCmd(original_movie, result_movie, fontfiles, texts, fontsizes, fontcolors, xs, ys, ss, es)
    the_cmd = the_instance.all_cmd()
    print(the_cmd)

    ret = subprocess.call(the_cmd, shell=True)
    assert ret == 0



class SubtitleCmd():
    
    def __init__(self, original_movie, result_movie, fontfiles, texts, fontsizes, fontcolors, xs, ys, ss, es):
        
        self.original_movie = original_movie
        self.result_movie = result_movie
        self.fontfiles = list(fontfiles)
        self.texts = list(texts)
        self.fontsizes = list(fontsizes)
        self.fontcolors = list(fontcolors)
        self.xs = list(xs)
        self.ys = list(ys)
        self.ss = list(ss)
        self.es = list(es)
        
        self.num_subtitles = len(self.texts)
        assert len(self.fontfiles)==self.num_subtitles
        assert len(self.fontsizes)==self.num_subtitles
        assert len(self.fontcolors)==self.num_subtitles
        assert len(self.xs)==self.num_subtitles
        assert len(self.ys)==self.num_subtitles
        assert len(self.ss)==self.num_subtitles
        assert len(self.es)==self.num_subtitles
        
        self.all_subtitile_args = []
        for i in range(self.num_subtitles):
            d = {
                "fontfile" : self.fontfiles[i],
                "text" : self.texts[i],
                "fontsize" : self.fontsizes[i],
                "fontcolor" : self.fontcolors[i],
                "x" : self.xs[i],
                "y" : self.ys[i],
                "s" : self.ss[i],
                "e" : self.es[i]
                }
            self.all_subtitile_args.append(d)
        
    
    def drawtext(self, fontfile, text, fontsize, fontcolor, x, y, s, e):
        # "drawtext={}"の部分、１つの文字列
        enable = "between(t, {}, {})".format(s, e)
        one_draw = "drawtext=fontfile={}: text={}: fontsize={}: fontcolor={}: x={}: y={}: enable='{}'".format(fontfile, text, fontsize, fontcolor, x, y, enable)
        print(one_draw)
        return one_draw
    
    def drawtext_all(self):
        # "drawtext={}"の部分の全ての文字列を作成
        drawtext_all = self.drawtext(**self.all_subtitile_args[0])  # 最初のテロップのみのdrawtextコマンド
        if len(self.all_subtitile_args) != 1:
            for args in self.all_subtitile_args[1:]:
                drawtext_all += ", "
                drawtext_all += self.drawtext(**args)
                
        return drawtext_all
    
    
    def all_cmd(self):
        
        drawtext_all = self.drawtext_all()
        all_cmd = 'ffmpeg -y -i {} -vf "{}" {}'.format(self.original_movie, drawtext_all, self.result_movie)
        print(all_cmd)
        
        return all_cmd
        
