#!/user/bin/env python 
# -*- coding: utf-8 -*-

from flask import Blueprint
app = Blueprint("static", __name__,
    static_url_path='/static', static_folder='./static'
)