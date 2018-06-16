#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2

def get_length_of_video(video_name):
    cap = cv2.VideoCapture(video_name)            # 動画を読み込む
    video_frame = cap.get(cv2.CAP_PROP_FRAME_COUNT) # フレーム数を取得する
    video_fps = cap.get(cv2.CAP_PROP_FPS)           # FPS を取得する
    video_len_sec = video_frame / video_fps                     # 長さ（秒）を計算する
    return video_len_sec