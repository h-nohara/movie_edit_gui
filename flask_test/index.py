#!/user/bin/env python 
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request
app = Flask(__name__, static_folder="sozai") #インスタンス生成

import os, sys, glob2, subprocess, shutil
from decimal import Decimal, ROUND_HALF_UP
import numpy as np
import pandas as pd
from pandas import DataFrame, Series
import re
import json


# static folderを追加
# Blueprintを読み込む
import static_config
app.register_blueprint(static_config.app)


# import python_src
# from python_src.make_silent_judge_dataframe import make_silent_judge_dataframe
# from python_src.music_movie_handlers.video_handlers.split_movie import split_movie
# from python_src.music_movie_handlers.video_handlers.insert_telop import insert_telop, fontfile_sample
# from python_src.music_movie_handlers.video_handlers.insert_WordImage import insert_WordImage


############################  自分で記述
# movie_name = "sozai/otoawase_ai3.mp4"
movie_name = "sozai/original.mp4"
sound_name = "sozai/original/original.wav"

use_voice_recog = False

# プロセスの中で作成されるファイル一覧
made_files = [
    "volume_judge.csv",
    "final.csv",
    "user_edited.csv",
    # もし音声認識を使った場合
    "recognized.csv",
]


# 無音判定を実行orしないを選択する画面
@app.route("/")
def SoundJudge_or_not():
    
    from python_src.run_localhost import run_localhost_at_subprocess
    run_localhost_at_subprocess()  # ローカルホストを立ち上げる

    return render_template("SoundJudge_or_not.html", movie_name=movie_name)


# 無音判定を実行
# 音声認識を実行orしないを選択する画面へ
@app.route("/SoundRecog_or_not/<select>")
def SoundRecog_or_not(select):
    
    if select == "do_Soundjudge":
        from python_src.make_silent_judge_dataframe import make_silent_judge_dataframe
        from python_src.where_to_cut_funcs import transform_for_working_table
        make_silent_judge_dataframe(original_movie=movie_name, result_csv="./sozai/volume_judge.csv", threshold=0.01)  # 無音判定
        df_silent_judge = pd.read_csv("./sozai/volume_judge.csv", index_col=0)  # 今作ったデータフレームを読み込み
        df_silent_judge_for_working_table = transform_for_working_table(df_silent_judge)  # working tableで使用できる形に
        df_silent_judge_for_working_table.to_csv("./sozai/volume_judge_for_working_table.csv")  # 保存

    return render_template("SoundRecog_or_not.html", movie_name=movie_name)


# # 音声認識を実行する
# # 音声認識の結果を編集する画面へ
@app.route("/start_SoundRecog", methods=["POST"])
def start_SoundRecog():
    
    # 音声の再生速度を受け取る

    receive = request.form
    temp = list(receive.keys())
    json_str = temp[0]
    result_dict = json.loads(json_str, encoding="utf-8")
    tempo = float(result_dict["tempo"])
    print("tempo : {}".format(tempo))
    
    
    from python_src.music_movie_handlers.video_handlers.split_movie import split_movie, concat_movie
    from python_src.music_movie_handlers.video_handlers.get_length_of_video import get_length_of_video
    from python_src.use_google_api.speech_api.recognize_with_timeoffset_Class import Sound_Recognize

    from python_src.music_movie_handlers.music_handlers.split_music import split_music
    from python_src.music_movie_handlers.music_handlers.change_tempo_music import change_tempo_music

    from python_src.where_to_cut_funcs import check_where_to_split

    # 音量判定のcsvを読み込み
    df = pd.read_csv("./sozai/volume_judge.csv", index_col=0)
    
    where_to_cut = []
    for i in range(df.shape[0]):
        s = float(Decimal(df.iloc[i]["start_time"]).quantize(Decimal("0.000"), rounding=ROUND_HALF_UP))
        e = float(Decimal(df.iloc[i]["end_time"]).quantize(Decimal("0.000"), rounding=ROUND_HALF_UP))
        where_to_cut.append([s, e])


    # 音声を分割して、保存する
    split_sound_dir = os.path.join(os.path.dirname(movie_name), "split_sounds")
    if os.path.exists(split_sound_dir):
        shutil.rmtree(split_sound_dir)
    os.makedirs(split_sound_dir)
    
    split_music(sound_name, where_to_cut, split_sound_dir, "wav")


    # 速度を変更した音声を保存
    for i in range(len(where_to_cut)):
        mini_sound = os.path.join(split_sound_dir, "split{0:03d}.wav".format(i))  # 分割された音声ファイル名
        slow_sound = os.path.join(split_sound_dir, "slow{0:03d}.wav".format(i))  # テンポを変えた音声ファイル名
        change_tempo_music(mini_sound, tempo, slow_sound)  # テンポを変更した音声ファイルを保存

    
    # 音声認識を実行

    print("start sound recognization ===========================================")

    def get_time(sound_name, bucket_name, bucket_save_path):
        sr = Sound_Recognize(wav=sound_name)
        sr.save_to_cloud_storage(bucket_name=bucket_name, bucket_save_path=bucket_save_path)
        sr.recognize()
        word_time_list = sr.word_time_list
        return word_time_list

    results = []
    slow_sounds = sorted(glob2.glob(os.path.join(split_sound_dir, "slow*.wav")))
    for slow_sound in slow_sounds:
        bucket_save_path = "slow_075/{}".format(os.path.basename(slow_sound))
        print(bucket_save_path)
        
        try:
            result = get_time(sound_name=slow_sound, bucket_name="for_mp3", bucket_save_path=bucket_save_path)
        except:
            result = "no_result"

        results.append(result)
        print(result)


    print("音声認識が終わりました。データフレームを作成します")
    print("="*100)
    

    # 結果の秒数を補正して、それぞれデータフレームに

    result_dfs = []
    for i, r in enumerate(results):
        df_result_one_chunk = DataFrame()
        the_base_start_time = float(Decimal(df.iloc[i]["start_time"]).quantize(Decimal("0.000"), rounding=ROUND_HALF_UP))
        the_base_end_time = float(Decimal(df.iloc[i]["end_time"]).quantize(Decimal("0.000"), rounding=ROUND_HALF_UP))
        if r=="no_result":
            df_result_one_chunk["word"] = ["no_result"]
            df_result_one_chunk["start_time"] = [the_base_start_time]
            df_result_one_chunk["end_time"] = [the_base_end_time]
            result_dfs.append(df_result_one_chunk)
        else:
            df_result_one_chunk["word"] = [chunk[0] for chunk in r]
            df_result_one_chunk["start_time"] = np.array([chunk[1] for chunk in r], dtype=float) * tempo + the_base_start_time
            df_result_one_chunk["end_time"] = np.array([chunk[2] for chunk in r], dtype=float) * tempo + the_base_start_time
            result_dfs.append(df_result_one_chunk)

    df_recognized = pd.concat(result_dfs)
    df_recognized = df_recognized.reset_index(drop=True)

    df_recognized.index = list(df_recognized["word"])
    del df_recognized["word"]
    df_recognized = df_recognized[["start_time", "end_time"]]
    df_recognized.to_csv("./sozai/recognized.csv")  # 念のためここで一旦保存

    df_recognized = check_where_to_split(df=df_recognized, span=2.0)
    df_recognized.to_csv("./sozai/recognized.csv")

    print("データフレームが保存されました")


    # 削除
    shutil.rmtree(split_sound_dir)

    return render_template("edit_recog_result.html", movie_name=movie_name)



# 音声認識の結果を編集する画面へ（音声認識を実行しない場合）
@app.route("/edit_recog_result")
def edit_recog_result():
    return render_template("edit_recog_result.html", movie_name=movie_name)


# 最後のワーキングテーブルへ
@app.route("/save_edited_sentence/<hoge>", methods=["POST", "GET"])
def working_table(hoge):
    
    from python_src.where_to_cut_funcs import split_and_to_block, transform_for_working_table


    receive = request.form
    temp = list(receive.keys())
    json_str = temp[0]
    result = json.loads(json_str, encoding="utf-8")

    

    df = DataFrame({
        "start_time": result["start_time"],
        "end_time": result["end_time"],
        "word": result["word"],
        "is_split": result["split"],
    })

    df.index = list(df["word"])
    df_blocked = split_and_to_block(df)
    df_for_working_table = transform_for_working_table(df_blocked)

    df_for_working_table.to_csv("./sozai/for_working_table.csv")
    print("saved ./sozai/for_working_table.csv")
    return "hoge"



# 最後のワーキングテーブルへ
@app.route("/working_table")
def to_working_table():
    return render_template("working_table.html", sound_name=sound_name, movie_name=movie_name)




# テーブルの内容をfinal.csvとして保存する
@app.route("/save_final_df", methods=["POST"])
def receive_final_df():

    # temp = list(request.forms.decode())
    print("%"*20)
    receive = request.form
    temp = list(receive.keys())
    
    json_str = temp[0]
    result = json.loads(json_str, encoding="utf-8")

    
    df = DataFrame({
        "start_time": result["s"],
        "end_time": result["e"],
        "word": result["w"],
        "is_use": result["is_use"],
        "is_telop": result["is_telop"],
        "font": result["font"],
        "fontsize": result["fontsize"],
        "color": result["color"],
        "recognized_word" : result["recognized_w"]
    })

    df = df.dropna()
    df.index = list(df.loc[:, "recognized_word"])
    df = df.loc[:, ["start_time", "end_time", "is_use", "is_telop", "word", "font", "fontsize", "color"]]
    df.to_csv("./sozai/final.csv")

    print("データフレームが保存されました")
    return "hoge"


# 動画を生成して良いか確認
@app.route("/check_to_create")
def check_to_create():
    return render_template("check_to_create.html")



# 最終的な動画ファイルを生成する
@app.route("/make_result_movie")
def make_result_movie():
    
    from python_src.music_movie_handlers.video_handlers.split_movie import split_one_movie, concat_movie
    from python_src.music_movie_handlers.video_handlers.insert_telop import insert_telop, fontfile_sample
    from python_src.music_movie_handlers.video_handlers.insert_WordImage import insert_WordImage
    from python_src.font_config import font_dict
    from python_src.color_config import color_dict
    
    among_time = 0.3  # among_time以内ならひとまとめにする

    # データフレームを読み込み
    df = pd.read_csv("sozai/final.csv", index_col=0)
    df = df[df["is_use"] == 1]

    # フォントファイルや位置のカラムをプログラム用に変換するコードを加える！
    df["font"] = df["font"].replace(font_dict)
    
    # 分割の位置を決めてそれぞれデータフレームに
    before_endtime = None
    split_numbers = [0]
    for i in range(df.shape[0]):
        start_time = df.iloc[i]["start_time"]
        end_time = df.iloc[i]["end_time"]
        if before_endtime is not None:
            if (start_time - before_endtime) >= among_time:
                split_numbers.append(i)
        before_endtime = end_time

    dfs = [df.iloc[split_numbers[i]:split_numbers[i+1]] for i in range(len(split_numbers)-1)]
    dfs.append(df.iloc[split_numbers[-1]:])

    # 分割する動画の保存場所
    mini_movie_dir = os.path.join(os.path.dirname(movie_name), "mini_movies")
    if os.path.exists(mini_movie_dir):
        shutil.rmtree(mini_movie_dir)
    os.makedirs(mini_movie_dir)

    for i, mini_df in enumerate(dfs):

        # 分割する
        mini_movie = os.path.join(mini_movie_dir, "mini_movie_{0:03d}.mp4".format(i))
        split_one_movie(original_movie=movie_name, where_to_cut=[list(mini_df["start_time"])[0], list(mini_df["end_time"])[-1]], result_movie=mini_movie)

        # テロップを入れる
        mini_df_telop = mini_df[mini_df["is_telop"]==1]
        if mini_df_telop.shape[0] > 0:
            whole_start_time = list(mini_df["start_time"])[0]
            mini_df_telop[["start_time", "end_time"]] = mini_df_telop[["start_time", "end_time"]] - whole_start_time

            # 元の動画をリネーム
            mini_movie_old = os.path.join(os.path.dirname(mini_movie), "_"+os.path.basename(mini_movie))
            os.rename(mini_movie, mini_movie_old)


            colors = color_dict(list(mini_df_telop["color"]))
            temporal_stroke_ws = []
            for color in colors:
                if len(color) == 3:
                    temporal_stroke_ws.append([9, 7])
                elif len(color) == 2:
                    temporal_stroke_ws.append([3])

            # テロップ入りの動画を生成
            insert_WordImage(
                original_movie = mini_movie_old,
                result_movie = mini_movie,
                fontfiles = mini_df_telop["font"],
                texts = mini_df_telop["word"],
                fontsizes = mini_df_telop["fontsize"],
                # fontcolors = [["pink", "pink", "white"]] * mini_df_telop.shape[0],
                fontcolors = colors,
                stroke_ws = temporal_stroke_ws,
                xs = ["middle"] * mini_df_telop.shape[0],
                ys = np.array(list(mini_df_telop["fontsize"]))*-1 + 1080 - 30,
                ss = mini_df_telop["start_time"],
                es = mini_df_telop["end_time"]
            )

    # 結合
    mini_movies = sorted(glob2.glob(os.path.join(mini_movie_dir, "mini_movie*.mp4")))
    concat_movie(mini_movies, os.path.join(os.path.dirname(movie_name), "result.mp4"))

    # 削除
    # if os.path.exists("sozai/original/"):
    #     shutil.rmtree("sozai/original/")

    print("完成品ができました")
    return "hoge"




if __name__ == "__main__":
    app.run(host="localhost", port=8090, debug=True)







# 必須

# @app.route("/<filepath:path>", name="static_file")
# def the_video(filepath):
#     return static_file(filepath, root="./")

# @app.route("/static/<filepath:path>", name="static_file")
# def static(filepath):
#     return static_file(filepath, root="./static")

# @app.route("/sozai/<filepath:path>", name="static_file")
# def static_sozai(filepath):
#     return static_file(filepath, root="./sozai/")

# @app.route("/d3/<filepath:path>", name="static_file")
# def static_d3(filepath):
#     return static_file(filepath, root="./d3/")

