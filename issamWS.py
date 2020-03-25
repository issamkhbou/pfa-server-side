from flask import Flask, flash, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
import os
import psycopg2
import cv2
import numpy as np
import re
import base64


from facerec_from_webcam import detect_faces_in_image
import face_recognition

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = "D:\\2019\\python\\face_recognition-master\\face_recognition-master\\examples\\train_dir"
UPLOAD_FOLDER_STUDENTS = "D:\\2019\\python\\face_recognition-master\\face_recognition-master\\examples"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pfa.db'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)
ma = Marshmallow(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    classe = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.png')

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"
    
    def serialize(self):
        return {"id": self.id,
                "username": self.username,
                "classe": self.classe,
                "email": self.email,
                "password": self.password,
                "image_file": self.image_file,
                
                } 

class UserSchema(ma.ModelSchema) : 
    class Meta : 
        model = User 




"""@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # print(filename)  # test.jpg
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print("Image saved")
            frame = face_recognition.load_image_file(UPLOAD_FOLDER+"\\"+filename)
            print(detect_faces_in_image(frame))
    return '''
    <!doctype html>
    <title>take a picture </title>
    <h1>Upload a picture </h1>
    <form method="POST" enctype="multipart/form-data">
      <input type="file" name="file">
      <input type="submit" value="Upload">
    </form>
    '''
"""


@app.route('/imageDetection', methods=['POST', 'GET'])
def upload():
    file = request.files['Image']
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    print("image saved")

    frame = face_recognition.load_image_file(UPLOAD_FOLDER+"\\"+filename)
    studentsNames = detect_faces_in_image(frame)
    print(studentsNames)
    # TODO for i in students :  studentsObj.append(filterby(i))
    return jsonify({
        "students": studentsNames})



# image uploaded by the teacher 
@app.route('/uploadAndDetectionImage', methods=['GET', 'POST'])
def api_save_base64_image():
    data = request.json
    file = data['img']
    id = data['id']
    starter = file.find(',')
    image_data = file[starter+1:]
    image_data = bytes(image_data, encoding="ascii")
    newFileName = 'test'+str(id)+".jpg"
    with open('train_dir\\'+newFileName, 'wb') as fh:
        fh.write(base64.decodebytes(image_data))

    frame = face_recognition.load_image_file(UPLOAD_FOLDER+"\\"+newFileName)
    studentsNames = detect_faces_in_image(frame)
    print(studentsNames)
    return jsonify({
        "students": studentsNames})



@app.route('/addStudent', methods=['POST', 'GET'])
def addStudent():
    req_data = request.json
    id = req_data['id']
    username = req_data['username']
    classe = req_data['classe']
    email = req_data['email']
    password = req_data['password']
    print(id)

    file = req_data['img']
    starter = file.find(',')
    image_data = file[starter+1:]
    image_data = bytes(image_data, encoding="ascii")
    newFileName = req_data['username'] + ".jpg"
    with open(newFileName, 'wb') as fh:
        fh.write(base64.decodebytes(image_data))

    student = User(id=id , username = username , classe = classe , email = email , password = password , image_file =UPLOAD_FOLDER_STUDENTS + newFileName  )
    db.session.add(student)
    db.session.commit()
    print (User.query.all())
    return jsonify({
        "msg": "student added"})


#get all students
@app.route('/getAllStudents', methods=['POST', 'GET'])
def getAllStudents():
    
    return jsonify({"students" : list(map(lambda user: user.serialize(), User.query.all()))}) 


@app.route('/student/<int:id>', methods=['DELETE'])
def delete_student(id):
    db.session.delete(User.query.get(id))
    db.session.commit()
    return jsonify({'result': True})


@app.route('/student/<int:id>', methods=['PUT'])
def update_user(id):
    user = User.query.get(id)
    user.id = request.json.get('id', user.id) #2nd is for the default 
    user.username = request.json.get('username', user.username) #2nd is for the default 
    user.classe = request.json.get('classe', user.classe) #2nd is for the default 
    user.email = request.json.get('email', user.email) #2nd is for the default 
    user.password = request.json.get('password', user.password) #2nd is for the default 
    db.session.commit()
    return jsonify({'user': user.serialize()})

if __name__ == '__main__':
    # * --- DEBUG MODE: --- *
    app.run(host='127.0.0.1', port=5000, debug=True)
