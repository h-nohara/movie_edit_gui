#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import pydub
from pydub import AudioSegment


'''
pydubで音声ファイルを読み込んで、長さを取得する関数
'''

def read_music_pydub(music):
    
    ext = os.path.splitext(music)[-1].split(".")[-1]
    music_obj = AudioSegment.from_file(music, format=ext)
    return music_obj


def get_length_of_music(music):

    sound = read_music_pydub(music)
    length_s = sound.duration_seconds
    
    return length_s