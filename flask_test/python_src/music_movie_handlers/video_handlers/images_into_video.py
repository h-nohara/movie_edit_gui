#!/user/bin/env python 
# -*- coding: utf-8 -*-

import os, sys, subprocess


def images_into_movie(original_movie, result_movie, images, xs, ys, ss, es):
    
    the_inst = ImagesIntoMovie(
        original_movie=original_movie, result_movie=result_movie,
        images=images,
        xs=xs, ys=ys,
        ss=ss, es=es
        )

    the_cmd = the_inst.all_cmd()
    print(the_cmd)

    ret = subprocess.call(the_cmd, shell=True)
    assert ret == 0



class ImagesIntoMovie:
    
    def __init__(self, original_movie, result_movie, images, xs, ys, ss, es):
        
        self.original_movie = original_movie
        self.result_movie = result_movie
        self.images = list(images)
        self.xs = list(xs)
        self.ys = list(ys)
        self.ss = list(ss)
        self.es = list(es)


    def input_files(self, images):
        
        input_cmd = "-i {}".format(self.original_movie)

        for image in images:
            input_cmd += " -i {}".format(image)
        
        return input_cmd

    
    def overlay_one(self, filter_head, x, y, s, e):
        
        if x == "middle":
            x = "(W-w)/2"
        if y == "middle":
            y = "(H-h)/2"

        temp_cmd = "{} overlay={}:{}:enable='between(t, {}, {})'".format(filter_head, x, y, s, e)
        return temp_cmd

    
    def overlay_all(self, xs, ys, ss, es):
                
        for i, image in enumerate(xs):
            
            if i == 0:
                filter_head = "[0:v][1:v]"
            else:
                filter_head = "[a];[a][{}:v]".format(i+1)

            overlay_one = self.overlay_one(filter_head=filter_head, x=xs[i], y=ys[i], s=ss[i], e=es[i])

            if i == 0:
                overlay_all = overlay_one
            else:
                overlay_all += overlay_one

        return overlay_all

    
    def all_cmd(self):
        
        input_files = self.input_files(self.images)
        overlay_all = self.overlay_all(xs=self.xs, ys=self.ys, ss=self.ss, es=self.es)
        
        all_cmd = 'ffmpeg -y {} -filter_complex "{}" {}'.format(input_files, overlay_all, self.result_movie)

        return all_cmd



