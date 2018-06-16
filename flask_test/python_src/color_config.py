#!/user/bin/env python 
# -*- coding: utf-8 -*-


def color_dict(color_codes):
    
    '''
    カラーコードの配列をmake_WordImage関数に渡す時の形式（リスト）に変換する関数

    :param str color_codes: ３色の場合は"pink_white_pink" （外側_間_内側）、２色の場合は"white_pink"（外側_内側）みたいなコードが入ったリストライク

    :return: ３色の場合は["pink", "white", "pink"]　（[外側 間 内側]）、２色の場合は["white", "pink"]（[外側　内側]）みたいなリストを含むリスト
    :rtype: list_in_list
    '''


    color_codes = list(color_codes)

    color_lists = []

    for color_code in color_codes:

        listed = color_code.split("_")

        if len(listed) == 2:
            color_list = [listed[0], listed[1]]
        elif len(listed) == 3:
            color_list = [listed[0], listed[1], listed[2]]
        
        color_lists.append(color_list)


    return color_lists

