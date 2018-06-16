#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys
import pydub
from pydub import AudioSegment


def read_music_pydub(music):
     
    ext = os.path.splitext(music)[-1].split(".")[-1]
    music_obj = AudioSegment.from_file(music, format=ext)
    return music_obj


def mix_musics(base_music, effect_sounds, start_times, result_music):
    
    '''
    元の音声に複数の音声を重ねる関数

    :param str base_music: 土台となる音声ファイル
    :param list effect_sounds: 重ねる音声ファイル
    :param list start_times: 重ねる音声ファイルの開始時間
    :param str result_music: 保存する音声ファイル名
 
    >>> mix_musics(
        base_music = "base.wav",
        effect_sounds = ["effect1.mp3", "effect2.mp3"],
        start_times=[1, 5],
        result_music="mixed.mp3"
        )
    '''

    assert len(effect_sounds) == len(start_times)
    
    base = read_music_pydub(base_music)
    
    for effect_sound, start_time in zip(effect_sounds, start_times):
        effect_obj = read_music_pydub(effect_sound)
        start_time_ms = start_time * 1000
        base = base.overlay(effect_obj, start_time_ms)  # ベースの音声に別の音声を重ねる
        
    base.export(result_music)
    print("saved {}".format(result_music))



# 音量を変化させる
def change_loudness(sound, ratio):
    
    result_sound = sound + ratio_to_db(ratio)
    return result_sound


# sound1をsound2のratio倍の音量に調整する
def adjust_loudness(sound1, sound2, ratio):
    
    rms_ratio = sound2.rms / sound1.rms
    result_sound = sound1 + ratio_to_db(rms_ratio)  # まず、音量をsound2に揃える
    result_sound = change_loudness(result_sound, ratio)  # ratio倍する
    return result_sound
