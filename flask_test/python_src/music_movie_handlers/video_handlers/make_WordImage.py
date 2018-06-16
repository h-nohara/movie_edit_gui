#!/user/bin/env python 
# -*- coding: utf-8 -*-

import os, sys, subprocess


def make_WordImage(word, fontsize, fontfile, num_color, colors, stroke_ws, result_image, W=None, H=None):
    
    '''
    テキスト画像を生成する関数

    Args:

        :param string word : テキスト
        :param float fontsize : フォントサイズ
        :param str fontfile : フォント
        :param int num_color : 何色使うか
        :param list-like colors : それぞれの色。３色の場合は[外側の色、間の色、内側の色]、２色の場合は[外側の色、内側の色]の順番で入れる。
        :param list-like stroke_ws : フチの太さ。３色の場合は[外側の太さ、間の太さ]。２色の場合は[外側の太さ]。
        :param str result_image : 生成する画像の名前。
        :param float W : 画像の横幅
        :param float H : 画像の縦幅

    >>> make_WordImage("おはよう", 20, "/Library/...", 3, ["pink", "white", "pink"], [8,3], "result.png")

    '''
    
    inst = MakeWordImage(word, fontsize, fontfile, num_color, colors, stroke_ws, result_image, W=None, H=None)

    if num_color == 3:
        cmd = inst.all_cmd_3colors()
    elif num_color == 2:
        cmd = inst.all_cmd_2colors()
    print(cmd)

    ret = subprocess.call(cmd, shell=True)
    assert ret == 0



class MakeWordImage:
    
    def __init__(self, word, fontsize, fontfile, num_color, colors, stroke_ws, result_image, W=None, H=None):
        
        self.word = word
        self.fontsize = fontsize
        self.fontfile = "'" + fontfile + "'"
        self.num_color = num_color
        self.colors = list(colors)
        self.stroke_ws = list(stroke_ws)
        self.result_image = result_image
        self.W = W or self.fontsize*len(word) + 4  # 余白を取っておく？
        self.H = H or self.fontsize + 4  # 余白を取っておく？

        assert num_color == len(colors)
        assert len(stroke_ws) == num_color - 1



    # 一番細かい粒度の関数３つ
    def draw_cmd(self, fontsize, word):
        
        cmd = "-draw 'font-size {} text 0,0 {}'".format(fontsize, '"'+word+'"')
        return cmd

    def stroke_cmd(self, color, stroke_w):
        
        cmd = "-stroke {} -strokewidth {}".format(color, stroke_w)
        return cmd

    def fill_cmd(self, color):
        
        cmd = "-fill {}".format(color)
        return cmd


   # 真ん中の粒度の関数２つ
    def stroke_draw(self, color, stroke_w, fontsize, word):
        
        tmp_cmd = "{stroke} {draw}"

        stroke = self.stroke_cmd(color, stroke_w)
        draw = self.draw_cmd(fontsize, word)

        cmd = tmp_cmd.format(stroke=stroke, draw=draw)
        return cmd


    def fill_stroke_draw(self, fill_color, stroke_color, stroke_w, fontsize, word):
        
        tmp_cmd = "{fill} {stroke} {draw}"

        fill = self.fill_cmd(fill_color)
        stroke = self.stroke_cmd(stroke_color, stroke_w)
        draw = self.draw_cmd(fontsize, word)

        cmd = tmp_cmd.format(fill=fill, stroke=stroke, draw=draw)
        return cmd

    

    # 最終粒度の関数２つ
    def all_cmd_3colors(self):
        
        tmp_cmd = "convert -size {W}x{H} xc:none -font {fontfile} -gravity center {draw_1} {draw_2} {result_image}"

        draw_1 = self.stroke_draw(
            color=self.colors[0],
            stroke_w=self.stroke_ws[0],
            fontsize=self.fontsize,
            word=self.word
            )

        draw_2 = self.fill_stroke_draw(
            fill_color=self.colors[2],
            stroke_color=self.colors[1],
            stroke_w=self.stroke_ws[1],
            fontsize=self.fontsize,
            word = self.word
            )

        cmd = tmp_cmd.format(
            W = self.W,
            H=self.H,
            fontfile=self.fontfile,
            draw_1=draw_1,
            draw_2=draw_2,
            result_image=self.result_image
        )

        return cmd

    
    def all_cmd_2colors(self):
        
        tmp_cmd = "convert -size {W}x{H} xc:none -font {fontfile} -gravity center {draw_1} {result_image}"

        draw_1 = self.fill_stroke_draw(
            fill_color=self.colors[1],
            stroke_color=self.colors[0],
            stroke_w=self.stroke_ws[0],
            fontsize=self.fontsize,
            word = self.word
            )

        cmd = tmp_cmd.format(
            W = self.W,
            H=self.H,
            fontfile=self.fontfile,
            draw_1=draw_1,
            result_image=self.result_image
        )

        return cmd



