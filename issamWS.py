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
from json import dumps
from base64 import b64encode

import datetime
from facerec_from_webcam import detect_faces_in_image
import face_recognition
from generate_xlsx import generateXlsx
from send_email_to_teacher import send_mail_with_excel

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


""" def transformImageTostring () : 
    ENCODING = 'utf-8'
    IMAGE_NAME = 'spam.jpg'
    JSON_NAME = 'output.json'

    # first: reading the binary stuff
    # note the 'rb' flag
    # result: bytes
    with open(IMAGE_NAME, 'rb') as open_file:
        byte_content = open_file.read()

    # second: base64 encode read data
    # result: bytes (again)
    base64_bytes = b64encode(byte_content)

    # third: decode these bytes to text
    # result: string (in utf-8)
    base64_string = base64_bytes.decode(ENCODING)

    # optional: doing stuff with the data
    # result here: some dict
    raw_data = {IMAGE_NAME: base64_string}

    # now: encoding the data to json
    # result: string
    json_data = dumps(raw_data, indent=2) """


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
                "image_file": self.image_file,} 
    
    def equals (self,otherStudent) : 
        return  self.id == otherStudent.id 

    def exists (self , studentList) : 
        for s in studentList : 
            if self.equals(s) : 
                return True 
        return False 

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


""" @app.route('/imageDetection', methods=['POST', 'GET'])
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
        "students": studentsNames}) """



# image uploaded by the teacher 
@app.route('/uploadAndDetectionImage', methods=['GET', 'POST'])
def api_save_base64_image():
    data = request.json
    file = data['img']
    classe=data['classe']
    id = data['id'] # adding this to the file name 
    starter = file.find(',')
    image_data = file[starter+1:]
    image_data = bytes(image_data, encoding="ascii")
    newFileName = 'test'+str(id)+".jpg"
    with open('train_dir\\'+newFileName, 'wb') as fh:
        fh.write(base64.decodebytes(image_data))

    frame = face_recognition.load_image_file(UPLOAD_FOLDER+"\\"+newFileName)
    studentsNames = detect_faces_in_image(frame)
    print(studentsNames)


    presents=[]
    for studentName in studentsNames :
        """ user = User.query.filter_by(username=studentsName).first() """
        presents.append(User.query.filter_by(username=studentName).first())
    print(presents , type(presents))

    d = datetime.datetime.today()
    excelFileName = "Liste "+classe+" "+d.strftime('%d-%m-%Y')+".xlsx"
    #TODO should be replaced by all = User.query.all(class) 
    all = User.query.all()
    generateXlsx(excelFileName,all,presents)

    recipient_email="issamkha123@gmail.com"
    send_mail_with_excel(recipient_email,classe,excelFileName)


    # generating a spreadsheet containing all student-class list with non presents and sending it to an email 
    # non presents : ([allStudents(GI2S1)] - [presenStudents]) 
    # + presents in the list => order by name => saving in the spreadsheet => sending to teacher email  
    # email teacher is mentioned in the json object along side with the test image as well as its id  

    #return jsonify({'students' : presents})
    return jsonify({"students" : list(map(lambda user: user.serialize(), presents  ))}) 

    



@app.route('/addStudent', methods=['POST', 'GET'])
def addStudent():
    req_data = request.json
    id = req_data['id']
    username = req_data['username']
    classe = req_data['classe']
    email = req_data['email']
    password = req_data['password']
    #print(id)

    file = req_data['img']
    starter = file.find(',')
    image_data = file[starter+1:]
    image_data = bytes(image_data, encoding="ascii")
    newFileName = req_data['username'] + ".jpg"
    with open(newFileName, 'wb') as fh:
        fh.write(base64.decodebytes(image_data))

    student = User(id=id , username = username , classe = classe , email = email , password = password , image_file =UPLOAD_FOLDER_STUDENTS +"\\"+ newFileName  )
    db.session.add(student)
    db.session.commit()
    print (User.query.all())
    return jsonify({
        "msg": "student added"})


#get all students
@app.route('/getAllStudents', methods=['POST', 'GET'])
def getAllStudents():
    users = User.query.all()
    output = []
    for user in users : 
        userData = {}
        userData['id'] = user.id
        userData['username'] = user.username
        userData['email'] = user.email
        userData['classe'] = user.classe
        userData['password'] = user.password
        with open(user.image_file, "rb") as img_file:
            userImageConvertedTobase64String = base64.b64encode(img_file.read()).decode("utf-8")

        userData['image_file'] = userImageConvertedTobase64String 
        output.append(userData)
    return jsonify({'users' : output}) 

    #return jsonify({"students" : list(map(lambda user: user.serialize(), User.query.all()))}) 


#get the details of one user :
@app.route('/getOneStudent/<int:id>', methods=['GET'])
def getOneStudent(id):
    user = User.query.filter_by(id=id).first()
    if not user : 
        return jsonify({'message'  : 'No user found!'})
    userData = {}
    userData['id'] = user.id
    userData['username'] = user.username
    userData['email'] = user.email
    userData['classe'] = user.classe
    userData['password'] = user.password

    with open(user.image_file, "rb") as img_file:
        userImageConvertedTobase64String = base64.b64encode(img_file.read()).decode("utf-8")

    userData['image_file'] = userImageConvertedTobase64String 
    return jsonify({'user' : userData})




@app.route('/student/<int:id>', methods=['DELETE'])
def deleteStudent(id):
    student = User.query.get(id)
    os.remove(student.image_file)
    db.session.delete(student)
    db.session.commit()
    return jsonify({'result': student.username +" deleted successfully"})


#update a student
@app.route('/student/<int:id>', methods=['PUT'])
def update_user(id):
    user = User.query.get(id)

    user.id = request.json.get('id', user.id) #2nd is for the default 
    #rename the image if the name is changed
    newName= request.json.get('username') 
    if newName  : 
        user.username = newName
        currentPathImage = "\\".join(user.image_file.split('\\')[:-1])
        newImagePath =currentPathImage +"\\"+ newName+".jpg" 
        os.rename(user.image_file, newImagePath)
        user.image_file = newImagePath
        db.session.commit()


    user.classe = request.json.get('classe', user.classe) #2nd is for the default 
    user.email = request.json.get('email', user.email) #2nd is for the default 
    user.password = request.json.get('password', user.password) #2nd is for the default 

    #change the image (remove the old and save the new)
    file = request.json.get('img')
    if file :
        os.remove(user.image_file)
        starter = file.find(',')
        image_data = file[starter+1:]
        image_data = bytes(image_data, encoding="ascii")
        newFileName = user.username + ".jpg"
        with open(newFileName, 'wb') as fh:
            fh.write(base64.decodebytes(image_data)) 

    db.session.commit()
    return jsonify({'user': user.serialize()})

@app.route('/login', methods=['POST'])
def login():
    req_data = request.json
    email = req_data['email']
    password = req_data['password']
    #TODO
    return 


if __name__ == '__main__':
    # * --- DEBUG MODE: --- *
    app.run(host='127.0.0.1', port=5000, debug=True)
