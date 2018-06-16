import os,sys
from os import makedirs
import time
import shutil
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

from silent_cut_class import SilentCutClass
from movie_cut_class import MovieCut

argvs = sys.argv
fname = argvs[1]

block_size = float(argvs[2])  # 0.40推奨
threshold = float(argvs[3])  # 0.05推奨


def normalize(the_data):
    M = 1
    m = -1
    normalized = ((the_data - the_data.min()) /  (the_data.max() - the_data.min())) * (M - m) + m
    return normalized


video = MovieCut(fname=fname)  # 読み込み
video.do_all(block_size=block_size, threshold=threshold)