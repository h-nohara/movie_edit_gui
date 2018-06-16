#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, subprocess


def change_tempo_music(original_music, tempo, result_music):
    
    '''
    soxを使って、（音程を変えずに）音声の速度を変化させる

    >>> change_tempo_music("original.wav", 0.75, "result.wav")
    '''
    
    cmd = "sox {} {} tempo {}".format(original_music, result_music, tempo)
    print(cmd)

    ret = subprocess.call(cmd, shell=True)
    assert ret == 0
    print("saved {}".format(result_music))