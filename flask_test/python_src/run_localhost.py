#!/user/bin/env python 
# -*- coding: utf-8 -*-

import subprocess
import multiprocessing

def run_localhost_at_subprocess():
    
    def wake():
        subprocess.call("python -m http.server", shell=True)

    p = multiprocessing.Process(target=wake)
    p.start()

