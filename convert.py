import base64
from flask import Flask, flash, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
import os
import psycopg2
import cv2
import numpy as np
import re

app = Flask(__name__)


def convert_and_save(b64_string):
    with open("train_dir\\newSaved.png", "wb") as fh:
        fh.write(base64.decodebytes(b64_string.encode()))


def receive_and_save(base64_img) : 
    base64_img_bytes = base64_img.encode('utf-8')
    with open("train_dir\\newSaved.png", 'wb') as file_to_save:
        decoded_image_data = base64.decodebytes(base64_img_bytes)
        file_to_save.write(decoded_image_data)




@app.route('/uploadImage', methods=['GET', 'POST'])
def api_save_base64_image():
    data = request.json
    file = data['img']
    id = data['id']
    starter = file.find(',')
    image_data = file[starter+1:]
    image_data = bytes(image_data, encoding="ascii")
    with open('train_dir\\test'+str(id)+".jpg", 'wb') as fh:
        fh.write(base64.decodebytes(image_data))
        return  jsonify({
            "msg": "ok"})
    return 'error'





if __name__ == '__main__':
    # * --- DEBUG MODE: --- *
    app.run(host='127.0.0.1', port=5000, debug=True)
