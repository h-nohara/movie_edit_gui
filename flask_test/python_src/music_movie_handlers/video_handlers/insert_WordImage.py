#!/user/bin/env python 
# -*- coding: utf-8 -*-

import os, sys, shutil, subprocess, glob2

from .make_WordImage import make_WordImage
from .images_into_video import images_into_movie


def insert_WordImage(original_movie, result_movie, fontfiles, texts, fontsizes, fontcolors, stroke_ws, xs, ys, ss, es):
    
    '''
    :param str original_movie: テキスト画像を差し込む元の動画
    :param str result_movie: 完成した動画名
    :param list fontfiles: それぞれのテキストのフォントファイル
    :param list texts: それぞれのテキスト
    :param list fontsizes: それぞれのフォントのサイズ
    :param list_in_list fontcolors: [["red", "blue", "orange"], ["white", "red]]みたいな感じ。フォントを構成する色。
    :param list_in_list stroke_ws: [[3], [8,3]]みたいな感じ。 それぞれのフォントのフチの太さ。
    :param list xs: それぞれのx座標
    :param list ys: y座標
    :param list ss: 文字画像を入れる開始時刻
    :param list es: 文字画像を入れる終了時刻
    '''
    
    fontfiles = list(fontfiles)
    texts = list(texts)
    fontsizes = list(fontsizes)
    xs = list(xs)
    ys = list(ys)
    ss = list(ss)
    es = list(es)


    # 長さが会っているか確認
    length = len(fontfiles)
    assert (len(texts) == length) & (len(fontsizes) == length) & (len(xs) == length) & (len(ys) == length) & (len(ss) == length) & (len(es) == length)


    dir_name = os.path.dirname(result_movie)

    # テキスト画像を保存するディレクトリを作成
    textimg_dir = os.path.join(dir_name, "_textimages")
    if os.path.exists(textimg_dir):
        shutil.rmtree(textimg_dir)
    os.makedirs(textimg_dir)


    # テキストごとに画像を生成
    for i, inzip in enumerate(zip(fontfiles, texts, fontsizes, fontcolors, stroke_ws, xs, ys, ss, es)):
        
        fontfile, text, fontsize, fontcolor, stroke_w, x, y, s, e = inzip
        assert len(fontcolor)-1 == len(stroke_w)

        result_image = os.path.join(textimg_dir, "textimg{0:03d}.png".format(i))  # 保存する画像の名前
        
        # テキスト画像を生成
        make_WordImage(
            word = text,
            fontsize = fontsize,
            fontfile = fontfile,
            num_color = len(fontcolor),
            colors = fontcolor,
            stroke_ws = stroke_w,
            result_image = result_image
            )


    text_images = sorted(glob2.glob(os.path.join(textimg_dir, "textimg*.png")))

    # 動画にテキスト画像を差し込む
    images_into_movie(
        original_movie = original_movie,
        result_movie = result_movie,
        images = text_images,
        xs = xs,
        ys = ys,
        ss = ss,
        es = es
        )

    shutil.rmtree(textimg_dir)

