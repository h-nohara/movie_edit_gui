#!/user/bin/env python 
# -*- coding: utf-8 -*-

import subprocess

def mp4_to_sound(input_file, output_file, bitrate=128, channnel=1):
    
    '''
    チャンネル数を指定して動画から音声を抽出
    '''
    
    cmd = "ffmpeg -y -i {} -ab {}k -ac {} {}".format(input_file, bitrate, channnel, output_file)
    result = subprocess.call(cmd, shell=True)

    if result == 0:
        print("saved {}".format(output_file))
    else:
        raise ValueError("error : func mp4_to_sound")

